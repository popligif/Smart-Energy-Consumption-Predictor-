"""
UI component for calibrating rates, thresholds, benchmarks, and saving configurations (FR-7).
"""
import streamlit as st
from config.settings import ConfigSettings

def render_settings() -> None:
    """Renders the settings calibration dashboard in Streamlit."""
    st.header("⚙️ Operational Settings & Calibration")
    st.write("Configure electricity tariffs, carbon indexes, and technical thresholds. Changes propagate instantly.")
    
    settings_manager = ConfigSettings()
    current_settings = settings_manager.load_settings()
    
    # 1. Layout sections
    col_set_left, col_set_right = st.columns(2)
    
    with col_set_left:
        st.subheader("Financial & Environmental Indices")
        
        tariff = st.number_input(
            "Electricity Tariff Rate (INR / kWh)", 
            min_value=1.0, 
            max_value=50.0, 
            value=float(current_settings.get("electricity_tariff")),
            step=0.1
        )
        
        carbon_factor = st.number_input(
            "Grid Carbon Coefficient (kg CO₂ / kWh)",
            min_value=0.0,
            max_value=5.0,
            value=float(current_settings.get("carbon_factor")),
            step=0.01
        )
        
        st.subheader("Efficiency Benchmarks")
        
        target_pf = st.slider(
            "Target Power Factor Index",
            min_value=0.90,
            max_value=1.00,
            value=float(current_settings.get("target_power_factor")),
            step=0.01
        )
        
        eei_benchmark = st.number_input(
            "EEI Building Benchmark (kWh / occupant-hr)",
            min_value=0.01,
            max_value=2.00,
            value=float(current_settings.get("eei_benchmark")),
            step=0.01
        )

    with col_set_right:
        st.subheader("Technical Alert Sensitivity thresholds")
        
        pf_threshold = st.slider(
            "Power Factor Alert Threshold (Critical alert if lower)",
            min_value=0.80,
            max_value=0.95,
            value=float(current_settings.get("power_factor_threshold")),
            step=0.01
        )
        
        hvac_temp_threshold = st.slider(
            "HVAC Efficiency Temperature Target (°C)",
            min_value=18.0,
            max_value=28.0,
            value=float(current_settings.get("hvac_temp_threshold")),
            step=0.5
        )
        
        peak_multiplier = st.slider(
            "Peak Load Surge Multiplier (x median)",
            min_value=1.1,
            max_value=3.0,
            value=float(current_settings.get("peak_load_multiplier")),
            step=0.1
        )
        
        idle_threshold_kw = st.number_input(
            "Unoccupied Room Idle Waste Threshold (kW)",
            min_value=0.5,
            max_value=20.0,
            value=float(current_settings.get("idle_load_threshold_kw")),
            step=0.5
        )

    st.markdown("---")
    
    # 2. Saving settings
    if st.button("💾 Apply & Save Configuration", type="primary", use_container_width=True):
        new_configs = {
            "electricity_tariff": tariff,
            "carbon_factor": carbon_factor,
            "power_factor_threshold": pf_threshold,
            "hvac_temp_threshold": hvac_temp_threshold,
            "peak_load_multiplier": peak_multiplier,
            "idle_load_threshold_kw": idle_threshold_kw,
            "target_power_factor": target_pf,
            "eei_benchmark": eei_benchmark
        }
        
        if settings_manager.save_settings(new_configs):
            # Clear ALL st.cache_data so the new tariff/carbon propagate
            st.cache_data.clear()
            st.success("🎉 Configuration saved! KPIs, costs, and carbon figures are now recalculated.")
            st.rerun()
        else:
            st.error("Failed to save settings. Check permissions on config/settings.json.")
