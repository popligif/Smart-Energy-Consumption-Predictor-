"""
Service layer for explainable AI recommendation logic, financial savings estimators, and carbon ROI calculations (FR-5).
"""
import pandas as pd
from typing import Dict, Any, List
from services.data_service import DataService
from services.alert_service import AlertService
from services.optimization_service import OptimizationService

class RecommendationService:
    """Dynamic recommender engine generating explainable, quantitative energy mitigation items."""
    
    def __init__(self) -> None:
        self.data_service = DataService()
        self.alert_service = AlertService()
        self.opt_service = OptimizationService()

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Scans campus alert telemetry and schedules to synthesize explainable mitigation items."""
        df = self.data_service.load_dataset()
        settings = self.data_service.settings_manager.load_settings()
        tariff = settings.get("electricity_tariff")
        carbon_factor = settings.get("carbon_factor")
        target_pf = settings.get("target_power_factor")
        
        alerts = self.alert_service.scan_for_alerts()
        recommendations = []
        
        # 1. Power Factor Correction Recommendation
        # Group alerts by building to see where PF is critically low
        low_pf_alerts = [a for a in alerts if a["Category"] == "Electrical"]
        pf_buildings = set(a["Building"] for a in low_pf_alerts)
        
        for building in pf_buildings:
            b_df = df[df["Building"] == building]
            avg_current_pf = b_df["Power Factor"].mean()
            annual_cost = b_df["Dynamic Cost (INR)"].sum() * 365 / len(b_df) # Scale to annual
            
            # Mathematical savings: losses decrease as PF increases
            # Approx loss reduction = 1 - (avg_pf / target_pf)^2, let's assume 1.5% overall cost saving from avoiding penalty
            factor = max(0.0, 1.0 - (avg_current_pf / target_pf))
            est_annual_savings = annual_cost * factor * 0.5 + 12000.0  # add penalty avoidance baseline
            est_annual_carbon = (est_annual_savings / tariff) * carbon_factor
            
            recommendations.append({
                "Title": f"Install Automatic Capacitor Banks in {building}",
                "Category": "Electrical Infrastructure",
                "Trigger": f"Average Power Factor is {avg_current_pf:.3f}, falling below threshold.",
                "Details": f"Install a localized automatic power factor correction (APFC) capacitor bank at the main electrical intake of {building}.",
                "Annual Savings (INR)": round(est_annual_savings, 2),
                "Annual Carbon Offset (kg CO2)": round(est_annual_carbon, 2),
                "Confidence": "High",
                "Reasoning": (
                    f"Power factor is low ({avg_current_pf:.3f}) due to inductive motor and ballast loads. "
                    f"Correcting this to {target_pf:.2f} reduces reactive current overhead, improving transformer efficiency. "
                    f"Estimated savings calculated using standard PF scaling losses: Annual Cost * (1 - Current PF / Target PF) * 0.5 + surcharge penalties."
                )
            })
            
        # 2. HVAC Optimization Recommendation
        hvac_opps = self.opt_service.get_hvac_optimization_opportunities()
        if hvac_opps:
            # Group by building
            hvac_buildings = set(o["Building"] for o in hvac_opps)
            for building in hvac_buildings:
                b_opps = [o for o in hvac_opps if o["Building"] == building]
                daily_kwh_savings = sum(o["Estimated Hourly Savings (kWh)"] for o in b_opps)
                # Extrapolate daily savings to annual (assuming 250 academic operational days)
                est_annual_savings = daily_kwh_savings * tariff * 220
                est_annual_carbon = daily_kwh_savings * carbon_factor * 220
                
                recommendations.append({
                    "Title": f"Optimize HVAC Operating Schedules in {building}",
                    "Category": "HVAC Controls",
                    "Trigger": f"Detected {len(b_opps)} hours where HVAC is running in empty rooms or cool weather.",
                    "Details": f"Adjust thermostat setpoint benchmarks to {settings.get('hvac_temp_threshold')}°C and implement smart scheduling to auto-disable units during off-peak occupancy hours.",
                    "Annual Savings (INR)": round(est_annual_savings, 2),
                    "Annual Carbon Offset (kg CO2)": round(est_annual_carbon, 2),
                    "Confidence": "Medium",
                    "Reasoning": (
                        f"HVAC was run inefficiently for {len(b_opps)} hours. "
                        f"Increasing the cooling setpoint or shutting down units during periods of low occupancy "
                        f"saves an average of 50% of the HVAC power draw (extrapolated for 220 operational days in the academic calendar)."
                    )
                })

        # 3. Idle Load Shutoff Recommendation
        idle_alerts = [a for a in alerts if a["Category"] == "Idle Waste"]
        idle_buildings = set(a["Building"] for a in idle_alerts)
        for building in idle_buildings:
            b_alerts = [a for a in idle_alerts if a["Building"] == building]
            b_df = df[df["Building"] == building]
            avg_waste_kw = b_df[(b_df["Occupancy"] == 0) & (b_df["Energy Consumption"] > settings.get("idle_load_threshold_kw"))]["Energy Consumption"].mean()
            if pd.isna(avg_waste_kw):
                avg_waste_kw = 3.0
                
            # Extrapolate annual savings
            est_daily_savings = len(b_alerts) * (avg_waste_kw - settings.get("idle_load_threshold_kw"))
            est_annual_savings = est_daily_savings * tariff * 220
            est_annual_carbon = est_daily_savings * carbon_factor * 220
            
            recommendations.append({
                "Title": f"Implement Smart Lighting & Equipment Shutdown in {building}",
                "Category": "Unoccupied Operations",
                "Trigger": f"Energy spikes (avg {avg_waste_kw:.1f} kW) detected when building occupancy is zero.",
                "Details": f"Implement localized PIR motion sensors and centralized computer shutdown policies to ensure lights, computers, and fans are disabled when floors are empty.",
                "Annual Savings (INR)": round(est_annual_savings, 2),
                "Annual Carbon Offset (kg CO2)": round(est_annual_carbon, 2),
                "Confidence": "High",
                "Reasoning": (
                    f"Idle leaks were detected during {len(b_alerts)} unoccupied hours. "
                    f"Automating equipment and lighting shutdown for these empty windows yields significant, "
                    f"low-cost savings estimated by multiplying idle run hours with average waste kW and utility tariffs."
                )
            })

        # 4. Load Shifting (Workshop/Laboratory)
        shifting_opps = self.opt_service.get_load_shifting_recommendations()
        if shifting_opps:
            # Group by building
            shift_buildings = set(s["Building"] for s in shifting_opps)
            for building in shift_buildings:
                b_shifts = [s for s in shifting_opps if s["Building"] == building]
                total_shiftable_power = sum(s["Shiftable Power (kW)"] for s in b_shifts)
                # Extrapolate savings from peak-demand penalty avoidance (e.g. ₹150 per kW demand charge reduction)
                est_annual_savings = total_shiftable_power * 150.0 * 12  # monthly demand charge savings
                # Carbon offset is negligible for pure load shifting, but assume 2% transmission/grid losses saved
                est_annual_carbon = (total_shiftable_power * 1.5) * carbon_factor * 220 * 0.02
                
                recommendations.append({
                    "Title": f"Shift Heavy Lab & Workshop Loads in {building}",
                    "Category": "Demand Side Management",
                    "Trigger": f"Detected {len(b_shifts)} hours of heavy lab/workshop equipment operating during peak campus load windows.",
                    "Details": f"Reschedule heavy equipment and laboratory session blocks from the peak occupancy window (9:00 AM - 5:00 PM) to early morning (7:00 AM - 9:00 AM) or late afternoon.",
                    "Annual Savings (INR)": round(est_annual_savings, 2),
                    "Annual Carbon Offset (kg CO2)": round(est_annual_carbon, 2),
                    "Confidence": "High",
                    "Reasoning": (
                        f"Rescheduling {total_shiftable_power:.1f} kW of laboratory/workshop machinery reduces "
                        f"peak demand spikes on the main sub-station. This saves demand charges billed monthly by the electrical utility board."
                    )
                })
                
        # If no recommendation triggered, provide a default system baseline suggestion
        if not recommendations:
            recommendations.append({
                "Title": "Maintain High Efficiency Setpoints",
                "Category": "General Operations",
                "Trigger": "Campus electrical and operational parameters are within safe bounds.",
                "Details": "Continue monitoring energy consumption via the Energy Command Centre and conduct quarterly audits.",
                "Annual Savings (INR)": 0.0,
                "Annual Carbon Offset (kg CO2)": 0.0,
                "Confidence": "High",
                "Reasoning": "All campus indicators are green. Keeping current procedures active is sufficient."
            })
            
        return recommendations
