"""
Service layer for computing high-level executive dashboard metrics, health scores, and rankings (FR-2).
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from services.data_service import DataService

class DashboardService:
    """Computes KPIs, Campus Energy Health Score, rankings, and executive briefs."""
    
    def __init__(self) -> None:
        self.data_service = DataService()

    def get_executive_kpis(self) -> Dict[str, Any]:
        """Calculates core campus KPIs from the engineered dataset."""
        df = self.data_service.load_dataset()
        
        total_energy = df["Energy Consumption"].sum()
        total_cost = df["Dynamic Cost (INR)"].sum()
        total_carbon = df["Dynamic Carbon (kg CO2)"].sum()
        
        # Identify absolute peak load and its context
        peak_row_idx = df["Current Power (kW)"].idxmax()
        peak_row = df.loc[peak_row_idx]
        
        peak_load = peak_row["Current Power (kW)"]
        peak_building = peak_row["Building"]
        peak_time = peak_row["Timestamp"].strftime("%Y-%m-%d %H:%M")
        
        # Average consumption per hour across the dataset
        avg_hourly_consumption = df["Energy Consumption"].mean()
        
        return {
            "total_energy_kwh": total_energy,
            "total_cost_inr": total_cost,
            "total_carbon_kg": total_carbon,
            "peak_load_kw": peak_load,
            "peak_building": peak_building,
            "peak_time": peak_time,
            "avg_hourly_consumption_kwh": avg_hourly_consumption
        }

    def get_building_rankings(self) -> List[Dict[str, Any]]:
        """Rank buildings based on overall energy usage and efficiency indices (FR-2)."""
        df = self.data_service.load_dataset()
        
        rankings = []
        for building, group in df.groupby("Building"):
            total_consumption = group["Energy Consumption"].sum()
            total_cost = group["Dynamic Cost (INR)"].sum()
            total_carbon = group["Dynamic Carbon (kg CO2)"].sum()
            
            # Energy Efficiency Index (EEI): average energy per occupant per hour
            avg_occupancy = group["Occupancy"].mean()
            avg_occupancy = max(1, avg_occupancy) # Avoid division by zero
            eei = total_consumption / (avg_occupancy * len(group))
            
            avg_pf = group["Power Factor"].mean()
            
            rankings.append({
                "Building": building,
                "Total Consumption (kWh)": round(total_consumption, 2),
                "Total Cost (INR)": round(total_cost, 2),
                "Total Carbon (kg CO2)": round(total_carbon, 2),
                "Average Power Factor": round(avg_pf, 3),
                "Energy Efficiency Index (kWh/occupant-hr)": round(eei, 3)
            })
            
        # Rank by consumption descending
        return sorted(rankings, key=lambda x: x["Total Consumption (kWh)"], reverse=True)

    def calculate_campus_health_score(self) -> Dict[str, Any]:
        """
        Computes Campus Energy Health Score (0-100) based on four weighted indicators:
        - Power Factor Compliance (Weight: 30%)
        - HVAC Utilization Efficiency (Weight: 30%)
        - Occupancy Waste Management (Weight: 25%)
        - Carbon Emission Intensity (Weight: 15%)
        """
        df = self.data_service.load_dataset()
        settings = self.data_service.settings_manager.load_settings()
        
        # 1. Power Factor Score: Penalty if below threshold
        pf_threshold = settings.get("power_factor_threshold")
        avg_pf = df["Power Factor"].mean()
        if avg_pf >= 0.95:
            pf_score = 100.0
        elif avg_pf <= 0.80:
            pf_score = 50.0
        else:
            # Linear scaling between 0.80 (50) and 0.95 (100)
            pf_score = 50 + (avg_pf - 0.80) / (0.95 - 0.80) * 50
            
        # 2. HVAC Utilization Score: Penalize when AC is high but temp is low (<24) or occupancy is low (<5)
        # Check percentage of hours where AC count > 2 and (temp < hvac_temp_threshold OR occupancy < 5)
        temp_threshold = settings.get("hvac_temp_threshold")
        hvac_waste_records = df[(df["Running ACs"] > 2) & ((df["Temperature"] < temp_threshold) | (df["Occupancy"] < 5))]
        waste_ratio = len(hvac_waste_records) / len(df)
        hvac_score = max(0.0, 100.0 - (waste_ratio * 150)) # scale penalty factor
        
        # 3. Occupancy Waste Score (Idle Load): Penalize when occupancy is 0 but energy consumption > threshold
        idle_threshold = settings.get("idle_load_threshold_kw")
        idle_waste_records = df[(df["Occupancy"] == 0) & (df["Energy Consumption"] > idle_threshold)]
        idle_waste_ratio = len(idle_waste_records) / len(df)
        occupancy_score = max(0.0, 100.0 - (idle_waste_ratio * 200))
        
        # 4. Carbon Footprint Score: Performance relative to a nominal baseline (e.g. 50 kg/hour average)
        # Average emissions in kg per hour
        avg_hourly_carbon = df["Dynamic Carbon (kg CO2)"].mean()
        carbon_score = max(0.0, min(100.0, 100.0 - (avg_hourly_carbon - 15.0) * 2.0))
        
        # Weighted aggregate
        health_score = int(
            (pf_score * 0.30) + 
            (hvac_score * 0.30) + 
            (occupancy_score * 0.25) + 
            (carbon_score * 0.15)
        )
        
        return {
            "overall_score": health_score,
            "power_factor_score": round(pf_score, 1),
            "hvac_efficiency_score": round(hvac_score, 1),
            "occupancy_efficiency_score": round(occupancy_score, 1),
            "carbon_performance_score": round(carbon_score, 1)
        }

    def generate_executive_brief(self) -> str:
        """Generates a dynamic paragraph compiling campus performance, highlights, and warning flags."""
        kpis = self.get_executive_kpis()
        health = self.calculate_campus_health_score()
        rankings = self.get_building_rankings()
        
        highest_consumer = rankings[0]["Building"]
        highest_consumption = rankings[0]["Total Consumption (kWh)"]
        lowest_consumer = rankings[-1]["Building"]
        
        brief = (
            f"The MIET Smart Campus operates with an overall **Energy Health Score of {health['overall_score']}/100** today. "
            f"Total daily electricity consumption across the 6 tracked blocks is **{kpis['total_energy_kwh']:,.1f} kWh**, "
            f"amounting to an operational utility cost of **₹{kpis['total_cost_inr']:,.2f}** and generating a carbon footprint of "
            f"**{kpis['total_carbon_kg']:,.1f} kg CO₂**. "
            f"The **{highest_consumer}** remains the primary load source, consuming **{highest_consumption:,.1f} kWh** "
            f"(ranking 1st in demand), while the **{lowest_consumer}** is the most energy-efficient block. "
        )
        
        # Highlight technical alerts dynamically
        warnings = []
        if health["power_factor_score"] < 85:
            warnings.append("low average power factor compliance")
        if health["hvac_efficiency_score"] < 80:
            warnings.append("inefficient HVAC scheduling during off-peak temperatures")
        if health["occupancy_efficiency_score"] < 80:
            warnings.append("energy leaks in unoccupied rooms (idle load waste)")
            
        if warnings:
            brief += f"**Critical Management Action Needed:** Immediate maintenance attention is recommended regarding " + ", ".join(warnings) + "."
        else:
            brief += "The electrical infrastructure shows excellent compliance profiles with no immediate service actions required."
            
        return brief
