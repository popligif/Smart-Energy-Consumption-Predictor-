"""
UI component for Building-wise Drill-down and diagnostics.
"""
import streamlit as st
import plotly.express as px
from services.data_service import DataService
from services.alert_service import AlertService

def render_building_drilldown() -> None:
    st.header("🏢 Building Drill-Down Diagnostics")
    st.write("Deep-dive analytics for localized facility energy management.")
    
    data_svc = DataService()
    df = data_svc.load_dataset()
    
    alert_svc = AlertService()
    all_alerts = alert_svc.scan_for_alerts()
    
    buildings = sorted(df["Building"].unique())
    
    st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
    selected_building = st.selectbox("Select Facility for Diagnostics", options=buildings, index=0)
    
    # Filter data
    b_df = df[df["Building"] == selected_building].sort_values("Hour")
    b_alerts = [a for a in all_alerts if a["Building"] == selected_building]
    
    # KPIs
    total_kw = b_df["Energy Consumption"].sum()
    peak_kw = b_df["Energy Consumption"].max()
    avg_pf = b_df["Power Factor"].mean()
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:3px solid #10B981;">
            <div style="font-size:0.75rem;color:#94A3B8;font-weight:600;text-transform:uppercase;">Total Consumption</div>
            <div style="font-size:2rem;font-weight:800;color:#0F172A;">{total_kw:.1f}<span style="font-size:0.9rem;color:#64748B;"> kWh</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:3px solid #F59E0B;">
            <div style="font-size:0.75rem;color:#94A3B8;font-weight:600;text-transform:uppercase;">Peak Demand</div>
            <div style="font-size:2rem;font-weight:800;color:#0F172A;">{peak_kw:.1f}<span style="font-size:0.9rem;color:#64748B;"> kW</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:3px solid #06B6D4;">
            <div style="font-size:0.75rem;color:#94A3B8;font-weight:600;text-transform:uppercase;">Avg Power Factor</div>
            <div style="font-size:2rem;font-weight:800;color:#0F172A;">{avg_pf:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        alert_clr = "#EF4444" if len(b_alerts) > 0 else "#10B981"
        st.markdown(f"""
        <div class="kpi-card" style="border-top:3px solid {alert_clr};">
            <div style="font-size:0.75rem;color:#94A3B8;font-weight:600;text-transform:uppercase;">Active Alerts</div>
            <div style="font-size:2rem;font-weight:800;color:{alert_clr};">{len(b_alerts)}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    
    # Charts and tables
    col_chart, col_alerts = st.columns([1.5, 1], gap="large")
    
    with col_chart:
        st.subheader(f"24-Hour Load Profile")
        fig = px.area(
            b_df, x="Hour", y="Energy Consumption", 
            color_discrete_sequence=["#059669"],
            markers=True
        )
        fig.update_layout(
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            xaxis_title="Hour of Day", yaxis_title="Consumption (kW)",
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col_alerts:
        st.subheader(f"Localized Alerts")
        if not b_alerts:
            st.success("✅ No alerts for this facility.")
        else:
            for a in b_alerts[:5]:
                sev_color = "#EF4444" if a["Severity"] == "Critical" else "#F59E0B"
                st.markdown(f"""
                <div style="border-left:4px solid {sev_color};background:#F8FAFC;padding:12px;margin-bottom:8px;border-radius:6px;">
                    <div style="font-size:0.8rem;font-weight:700;color:#0F172A;">{a['Category']}</div>
                    <div style="font-size:0.75rem;color:#475569;margin-top:4px;">{a['Message']}</div>
                    <div style="font-size:0.7rem;color:#94A3B8;margin-top:6px;text-align:right;">Trigger: {a['Parameter']}</div>
                </div>
                """, unsafe_allow_html=True)
            if len(b_alerts) > 5:
                st.write(f"*(+{len(b_alerts)-5} more alerts not shown)*")
