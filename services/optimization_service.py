"""
Service layer for HVAC schedule optimization and shiftable load scheduling (FR-5).
"""
import pandas as pd
from typing import Dict, Any, List
from services.data_service import DataService

class OptimizationService:
    """Computes technical load shifting schedules and temperature setback opportunities."""
    
    def __init__(self) -> None:
        self.data_service = DataService()

    def get_hvac_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identifies periods where ACs are running in cool temperatures or empty floors."""
        df = self.data_service.load_dataset()
        settings = self.data_service.settings_manager.load_settings()
        tariff = settings.get("electricity_tariff")
        carbon_factor = settings.get("carbon_factor")
        temp_threshold = settings.get("hvac_temp_threshold")
        
        inefficient_runs = df[
            (df["Running ACs"] > 0) & 
            ((df["Temperature"] < temp_threshold) | (df["Occupancy"] == 0))
        ]
        
        opportunities = []
        for idx, row in inefficient_runs.iterrows():
            building = row["Building"]
            hour = row["Hour"]
            ac_count = row["Running ACs"]
            current_temp = row["Temperature"]
            current_occupancy = row["Occupancy"]
            current_hvac_load = row["HVAC Load"]
            
            # Estimate potential hourly savings by turning off/reducing 50% of ACs
            potential_hourly_saving_kwh = current_hvac_load * 0.5
            potential_hourly_saving_inr = potential_hourly_saving_kwh * tariff
            potential_hourly_saving_co2 = potential_hourly_saving_kwh * carbon_factor
            
            # Determine reason
            if current_occupancy == 0:
                reason = "Running ACs on an unoccupied floor"
            else:
                reason = f"Outdoor temperature is cool ({current_temp}°C); natural ventilation is sufficient"
                
            opportunities.append({
                "Building": building,
                "Hour": hour,
                "ACs Running": ac_count,
                "Temperature (°C)": current_temp,
                "Occupancy": current_occupancy,
                "HVAC Load (kW)": current_hvac_load,
                "Estimated Hourly Savings (kWh)": round(potential_hourly_saving_kwh, 2),
                "Estimated Savings (INR)": round(potential_hourly_saving_inr, 2),
                "Carbon Offset (kg CO2)": round(potential_hourly_saving_co2, 2),
                "Reason": reason
            })
            
        return opportunities

    def get_load_shifting_recommendations(self) -> List[Dict[str, Any]]:
        """Identifies heavy laboratory and workshop load runs during peak campus occupancy (FR-5)."""
        df = self.data_service.load_dataset()
        
        # Filter for heavy equipment usage (Lab/Workshop usage > 0) during peak tariff hours (9:00 AM to 5:00 PM)
        peak_heavy_loads = df[
            (df["Hour"] >= 9) & 
            (df["Hour"] <= 17) & 
            ((df["Laboratory Usage"] > 1.5) | (df["Workshop Usage"] > 1.5))
        ]
        
        recommendations = []
        for idx, row in peak_heavy_loads.iterrows():
            building = row["Building"]
            hour = row["Hour"]
            lab_usage = row["Laboratory Usage"]
            workshop_usage = row["Workshop Usage"]
            total_shiftable_power = lab_usage + workshop_usage
            
            # Shift window suggestion (e.g. shift to early morning 7-9 AM or late evening 6-9 PM)
            target_hour = 7 if hour < 13 else 18
            
            # Potential peak load shaving estimate
            shaved_demand_kw = total_shiftable_power * 0.8  # Assume 80% can be shifted successfully
            
            recommendations.append({
                "Building": building,
                "Peak Hour": hour,
                "Lab Load (kW)": round(lab_usage, 2),
                "Workshop Load (kW)": round(workshop_usage, 2),
                "Shiftable Power (kW)": round(total_shiftable_power, 2),
                "Suggested Shift Hour": f"{target_hour:02d}:00",
                "Peak Demand Shaving (kW)": round(shaved_demand_kw, 2),
                "Operational Impact": f"Reduces peak demand load on grid by {shaved_demand_kw:.1f} kW during grid strain hours."
            })
            
        return recommendations
