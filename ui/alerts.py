"""
UI component for displaying active Smart Alerts and efficiency warnings (FR-6).
"""
import streamlit as st
import pandas as pd
from services.alert_service import AlertService

def render_alerts() -> None:
    """Renders the Smart Alerts dashboard in Streamlit."""
    st.header("🔔 Operational Smart Alerts")
    st.write("Campus-wide telemetry watchdogs monitoring equipment leaks, power quality issues, and load surges.")
    
    alert_service = AlertService()
    alerts = alert_service.scan_for_alerts()
    
    # 1. Summary Statistics Cards
    tot_alerts = len(alerts)
    crit_alerts = len([a for a in alerts if a["Severity"] == "Critical"])
    warn_alerts = len([a for a in alerts if a["Severity"] == "Warning"])
    
    c_tot, c_crit, c_warn = st.columns(3)
    c_tot.metric("Total Active Alerts", tot_alerts)
    c_crit.metric("Critical Alerts", crit_alerts, delta_color="inverse")
    c_warn.metric("Warning Alerts", warn_alerts)
    
    st.markdown("---")
    
    # 2. Filter Alerts
    st.subheader("Filter Active Alerts")
    col_af1, col_af2, col_af3 = st.columns(3)
    
    with col_af1:
        severities = ["All", "Critical", "Warning"]
        selected_severity = st.selectbox("Filter by Severity", options=severities)
        
    with col_af2:
        buildings = ["All"] + sorted(list(set(a["Building"] for a in alerts)))
        selected_building = st.selectbox("Filter by Building", options=buildings)
        
    with col_af3:
        categories = ["All"] + sorted(list(set(a["Category"] for a in alerts)))
        selected_category = st.selectbox("Filter by Category", options=categories)
        
    # Apply filters
    filtered_alerts = alerts
    if selected_severity != "All":
        filtered_alerts = [a for a in filtered_alerts if a["Severity"] == selected_severity]
    if selected_building != "All":
        filtered_alerts = [a for a in filtered_alerts if a["Building"] == selected_building]
    if selected_category != "All":
        filtered_alerts = [a for a in filtered_alerts if a["Category"] == selected_category]
        
    # 3. Render Alerts Table / Cards
    if not filtered_alerts:
        st.success("✅ No active alerts matching the selected filters. Operations are operating within safe bounds.")
        return
        
    st.write(f"Showing {len(filtered_alerts)} active alerts:")
    
    for alert in filtered_alerts:
        sev_color = "#E53E3E" if alert["Severity"] == "Critical" else "#DD6B20"
        bg_color = "#FFF5F5" if alert["Severity"] == "Critical" else "#FFFAF0"
        
        st.markdown(
            f"""
            <div style="background-color: {bg_color}; border-left: 5px solid {sev_color}; padding: 16px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <span style="font-weight: 700; color: {sev_color}; text-transform: uppercase; font-size: 0.85rem;">
                        [{alert['Severity']}] {alert['Category']}
                    </span>
                    <span style="font-size: 0.75rem; color: #718096; font-weight: 500;">
                        🕒 {alert['Timestamp']}
                    </span>
                </div>
                <div style="font-size: 0.95rem; color: #2D3748; margin-bottom: 8px; line-height: 1.5;">
                    {alert['Message']}
                </div>
                <div style="display: flex; gap: 15px; font-size: 0.8rem; color: #4A5568; font-weight: 500;">
                    <span>📍 Building: <b>{alert['Building']}</b> (Hour: {alert['Hour']})</span>
                    <span>📊 Read Parameter: <b>{alert['Parameter']}</b></span>
                    <span>🎯 Limit: <b>{alert['Threshold']}</b></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
