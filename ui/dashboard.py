"""
UI component for the flagship Director Decision Centre & Executive Dashboard (FR-2).
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from services.dashboard_service import DashboardService
from services.alert_service import AlertService

def render_dashboard() -> None:
    """Renders the flagship Director Decision Centre dashboard in Streamlit."""
    db_service = DashboardService()
    alert_service = AlertService()
    
    # Load metrics
    kpis = db_service.get_executive_kpis()
    health = db_service.calculate_campus_health_score()
    brief = db_service.generate_executive_brief()
    rankings = db_service.get_building_rankings()
    alerts = alert_service.scan_for_alerts()
    
    # Executive Header with Styling
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #1A365D 0%, #2A4365 100%); padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.15)">
            <h1 style="color: white; margin: 0; font-family: 'Inter', sans-serif; font-size: 2.2rem;">Director Decision Centre</h1>
            <p style="color: #90CDF4; margin: 5px 0 0 0; font-size: 1.1rem; font-weight: 300;">MIET Smart Campus Energy Command & Operations Centre</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # User Persona Display
    role = st.session_state.get("user_role", "Director")
    st.info(f"🔑 Active Session Profile: **{role}** — Custom view calibrated to your management scope.")

    # 1. Health Score Section (Visual Gauge representation)
    st.subheader("Campus Energy Health rating")
    
    h_col1, h_col2 = st.columns([1, 2])
    with h_col1:
        score = health["overall_score"]
        # Custom HTML CSS Gauge
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background-color: #F7FAFC; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; text-align: center; height: 180px;">
                <span style="font-size: 0.9rem; color: #718096; font-weight: 600; text-transform: uppercase;">Health Score</span>
                <span style="font-size: 3.5rem; font-weight: 800; color: {'#38A169' if score >= 85 else ('#DD6B20' if score >= 70 else '#E53E3E')}; margin: 5px 0;">{score}</span>
                <span style="font-size: 0.85rem; color: #4A5568; font-weight: 500;">Scale 0 - 100</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with h_col2:
        # Score Breakdown Progress bars
        st.write("Score Card Breakdown:")
        st.progress(health["power_factor_score"]/100, text=f"Power Factor: {health['power_factor_score']}/100")
        st.progress(health["hvac_efficiency_score"]/100, text=f"HVAC Efficiency: {health['hvac_efficiency_score']}/100")
        st.progress(health["occupancy_efficiency_score"]/100, text=f"Occupancy Waste Management: {health['occupancy_efficiency_score']}/100")
        st.progress(health["carbon_performance_score"]/100, text=f"Carbon Footprint Index: {health['carbon_performance_score']}/100")
        
    st.markdown("---")
    
    # 2. Executive Brief Paragraph
    st.subheader("Daily Executive Brief")
    st.markdown(
        f"""
        <div style="background-color: #EBF8FF; border-left: 5px solid #3182CE; padding: 18px; border-radius: 6px; font-family: 'Inter', sans-serif; font-size: 1.05rem; line-height: 1.6; color: #2B6CB0;">
            {brief}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # 3. Main KPI Metrics
    st.subheader("Campus KPIs (Engested Data)")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Total Energy", f"{kpis['total_energy_kwh']:,.1f} kWh", help="Sum of energy consumed across monitored blocks.")
    m_col2.metric("Electricity cost", f"₹{kpis['total_cost_inr']:,.2f}", help="Cost calculated based on calibrated tariffs.")
    m_col3.metric("Carbon Emissions", f"{kpis['total_carbon_kg']:,.1f} kg CO2", help="Carbon footprint based on grid carbon factor settings.")
    m_col4.metric("Peak demand Load", f"{kpis['peak_load_kw']:,.1f} kW", f"{kpis['peak_building']}", help="Highest instantaneous power reading recorded.")

    st.markdown("---")
    
    # 4. Critical Warnings & Rankings
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("Building consumption rankings")
        df_rank = pd.DataFrame(rankings)
        fig = px.bar(
            df_rank, 
            y="Building", 
            x="Total Consumption (kWh)", 
            orientation="h",
            color="Total Consumption (kWh)",
            color_continuous_scale="Viridis",
            labels={"Total Consumption (kWh)": "kWh Used"},
            height=300
        )
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with col_right:
        st.subheader("Anomalies & Critical Warnings")
        # Filter for Critical alerts
        critical_alerts = [a for a in alerts if a["Severity"] == "Critical"]
        if not critical_alerts:
            st.success("✅ No critical operational or hardware alerts active today.")
        else:
            for alert in critical_alerts[:4]:
                st.markdown(
                    f"""
                    <div style="background-color: #FFF5F5; border-left: 4px solid #E53E3E; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                        <span style="font-weight: 700; color: #C53030; font-size: 0.9rem;">[CRITICAL] {alert['Category']} alert</span><br/>
                        <span style="font-size: 0.85rem; color: #742A2A;">{alert['Message']}</span><br/>
                        <span style="font-size: 0.75rem; color: #9B2C2C; font-style: italic;">Trigger: {alert['Parameter']} | {alert['Timestamp']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            if len(critical_alerts) > 4:
                st.write(f"*(And {len(critical_alerts) - 4} other critical alert records. Check Alerts section)*")
                
    # Footer quick action
    st.markdown(
        """
        <div style="text-align: center; margin-top: 40px; font-size: 0.85rem; color: #A0AEC0;">
            Meerut Institute of Engineering and Technology Smart Campus DSS • Version 1.0.0
        </div>
        """,
        unsafe_allow_html=True
    )
