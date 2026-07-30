"""
Service layer for identifying anomalies, efficiency flags, and electrical alert states (FR-6).
"""
import pandas as pd
from typing import Dict, Any, List
from services.data_service import DataService

class AlertService:
    """Scan engine for telemetry rules, flagging operational leaks and electrical thresholds."""
    
    def __init__(self) -> None:
        self.data_service = DataService()

    def scan_for_alerts(self) -> List[Dict[str, Any]]:
        """Scans dataset telemetry and triggers rule-based alerts based on administrator thresholds."""
        df = self.data_service.load_dataset()
        settings = self.data_service.settings_manager.load_settings()
        
        pf_threshold = settings.get("power_factor_threshold")
        temp_threshold = settings.get("hvac_temp_threshold")
        idle_threshold = settings.get("idle_load_threshold_kw")
        peak_multiplier = settings.get("peak_load_multiplier")
        
        alerts = []
        
        # Calculate baseline median consumption per building to detect spikes
        median_consumption = df.groupby("Building")["Energy Consumption"].median().to_dict()
        
        for idx, row in df.iterrows():
            building = row["Building"]
            hour = row["Hour"]
            timestamp = row["Timestamp"].strftime("%Y-%m-%d %H:%M")
            
            # Rule 1: Low Power Factor (Critical)
            pf = row["Power Factor"]
            if pf < pf_threshold:
                alerts.append({
                    "Timestamp": timestamp,
                    "Building": building,
                    "Hour": hour,
                    "Severity": "Critical",
                    "Category": "Electrical",
                    "Parameter": f"Power Factor: {pf:.3f}",
                    "Threshold": f"< {pf_threshold:.2f}",
                    "Message": (
                        f"Power Factor in {building} dropped to {pf:.3f} (Threshold: {pf_threshold:.2f}). "
                        f"This causes reactive power inefficiencies and risks power board penalties."
                    )
                })
                
            # Rule 2: HVAC Inefficiency (Warning)
            temp = row["Temperature"]
            running_acs = row["Running ACs"]
            hvac_load = row["HVAC Load"]
            if running_acs > 2 and temp < temp_threshold and hvac_load > 0:
                alerts.append({
                    "Timestamp": timestamp,
                    "Building": building,
                    "Hour": hour,
                    "Severity": "Warning",
                    "Category": "HVAC Inefficiency",
                    "Parameter": f"ACs Running: {running_acs} (Temp: {temp}°C)",
                    "Threshold": f"Temp < {temp_threshold}°C",
                    "Message": (
                        f"HVAC AC units are active ({running_acs} ACs) in {building} while the outdoor temperature "
                        f"is {temp}°C, violating the efficiency threshold of {temp_threshold}°C."
                    )
                })
                
            # Rule 3: Idle Load Waste (Critical)
            occupancy = row["Occupancy"]
            energy = row["Energy Consumption"]
            if occupancy == 0 and energy > idle_threshold:
                alerts.append({
                    "Timestamp": timestamp,
                    "Building": building,
                    "Hour": hour,
                    "Severity": "Critical",
                    "Category": "Idle Waste",
                    "Parameter": f"Energy: {energy:.2f} kW (Empty Room)",
                    "Threshold": f"< {idle_threshold:.2f} kW",
                    "Message": (
                        f"Energy consumption of {energy:.2f} kW detected in {building} while occupancy is zero. "
                        f"Indicates lights, computers, or ACs were left running on unoccupied floors."
                    )
                })
                
            # Rule 4: Peak Load Surge (Warning)
            baseline = median_consumption.get(building, 10.0)
            if energy > (baseline * peak_multiplier):
                alerts.append({
                    "Timestamp": timestamp,
                    "Building": building,
                    "Hour": hour,
                    "Severity": "Warning",
                    "Category": "Peak Load Spike",
                    "Parameter": f"Energy: {energy:.2f} kW (Baseline: {baseline:.2f} kW)",
                    "Threshold": f"> {peak_multiplier}x median",
                    "Message": (
                        f"Consumption spike detected in {building} ({energy:.2f} kW), which is "
                        f"{(energy / baseline):.1f}x higher than the typical baseline of {baseline:.2f} kW."
                    )
                })
                
            # Rule 5: Vacant Room — Camera Feed Triggered Guard Alert
            # Simulates smart camera occupancy detection: room nearly empty but ACs/lights still on
            lighting_load = row.get("Lighting Load", 0)
            floor = row.get("Floor", "Unknown")
            if occupancy <= 2 and (running_acs > 0 or lighting_load > 0.5):
                devices_on = []
                if running_acs > 0:
                    devices_on.append(f"{running_acs} AC unit(s)")
                if lighting_load > 0.5:
                    devices_on.append(f"Lighting ({lighting_load:.2f} kW)")
                devices_str = " and ".join(devices_on)

                alerts.append({
                    "Timestamp": timestamp,
                    "Building": building,
                    "Hour": hour,
                    "Floor": floor,
                    "Severity": "Critical",
                    "Category": "Vacant Room — Guard Alert",
                    "Parameter": f"Occupancy: {occupancy} | {devices_str} still ON",
                    "Threshold": "Occupancy ≤ 2 with active loads",
                    "Message": (
                        f"🎥 **Camera Feed Alert:** Room on **Floor {floor}, {building}** detected "
                        f"near-vacant (Occupancy: {occupancy}) at Hour {hour}:00, but {devices_str} "
                        f"are still running. Immediate manual shutdown required."
                    ),
                    "Guard_Action": (
                        f"📢 **Guard Dispatch Order:** Security personnel assigned to **Floor {floor} "
                        f"of {building}** — proceed to the nearest vacant room and manually switch off "
                        f"{devices_str}. Confirm shutdown via intercom/app within 15 minutes. "
                        f"If room remains occupied by ≤ 2 persons, verify with department coordinator "
                        f"before shutting down equipment."
                    ),
                })

        # Sort alerts: Critical first, then Warning, then by timestamp descending
        severity_order = {"Critical": 0, "Warning": 1, "Info": 2}
        return sorted(alerts, key=lambda x: (severity_order.get(x["Severity"], 2), x["Timestamp"]), reverse=True)
