"""
UI component for Load Optimization, HVAC setbacks, and load shifting recommendations (FR-5).
"""
import streamlit as st
import pandas as pd
from services.optimization_service import OptimizationService

def render_load_optimization() -> None:
    """Renders the Load Optimization tab in Streamlit."""
    st.header("🔌 Load Optimization & Scheduling")
    st.write(
        "Manage grid strain, avoid peak demand penalties, and optimize thermal appliance runtimes."
    )
    
    opt_service = OptimizationService()
    
    tab_shifting, tab_hvac = st.tabs([
        "📅 Shiftable Load Scheduling", 
        "❄️ HVAC Setpoint Optimization"
    ])
    
    with tab_shifting:
        st.subheader("Shiftable Machinery & Laboratory Scheduling")
        st.write(
            "Heavy laboratory and workshop induction machinery running during peak grid hours can "
            "be rescheduled to early morning or late evening off-peak periods to reduce peak charges."
        )
        
        shifts = opt_service.get_load_shifting_recommendations()
        if not shifts:
            st.success("✅ No heavy machinery loads detected during peak campus demand hours.")
        else:
            df_shifts = pd.DataFrame(shifts)
            st.dataframe(df_shifts, use_container_width=True)
            
            st.markdown(
                """
                > [!TIP]
                > **How to execute Load Shifting:** Reschedule lab batches in Academic Block B/C and Workshop sessions. 
                > Shifting these sessions by even 2 hours can shave up to 80% of peak machinery loads off the main substation meter.
                """
            )
            
    with tab_hvac:
        st.subheader("HVAC Thermostat Setpoint Calibration")
        st.write(
            "This utility identifies hours when cooling units are running on unoccupied floors "
            "or when outdoor temperatures are already cool, representing direct energy waste."
        )
        
        hvac_opps = opt_service.get_hvac_optimization_opportunities()
        if not hvac_opps:
            st.success("✅ HVAC cooling units are aligned with occupancy schedules and weather bounds.")
        else:
            df_hvac = pd.DataFrame(hvac_opps)
            
            # Filter display columns
            display_cols = [
                "Building", "Hour", "ACs Running", "Temperature (°C)", 
                "Occupancy", "HVAC Load (kW)", "Estimated Hourly Savings (kWh)", 
                "Estimated Savings (INR)", "Reason"
            ]
            st.dataframe(df_hvac[display_cols], use_container_width=True)
            
            # Show aggregated metrics
            tot_hvac_savings_inr = df_hvac["Estimated Savings (INR)"].sum()
            tot_hvac_savings_co2 = df_hvac["Carbon Offset (kg CO2)"].sum()
            
            st.info(
                f"💡 **Potential Operational Impact:** Implementing setback controls across these occurrences "
                f"would save approximately **₹{tot_hvac_savings_inr:,.2f}** and offset **{tot_hvac_savings_co2:.1f} kg CO₂** daily."
            )
