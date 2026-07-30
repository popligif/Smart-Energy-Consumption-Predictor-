"""
Main application router and entry point for the MIET Smart Campus Energy Command Centre.
"""
import streamlit as st
from config.logging import setup_logging
from config.settings import ConfigSettings

setup_logging()
settings_manager = ConfigSettings()

st.set_page_config(
    page_title="MIET Smart Campus Energy Management",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS Design System ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Reset & Base */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.main { background-color: #F0F4F8 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
    border-right: 1px solid #334155;
}
section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] .stRadio label { 
    color: #94A3B8 !important; font-size: 0.85rem !important; padding: 4px 0;
}
section[data-testid="stSidebar"] .stSelectbox label { color: #64748B !important; }

/* Cards */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.04);
    border: 1px solid #F1F5F9;
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.10);
}
.building-card {
    background: white;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    border: 1px solid #F1F5F9;
    border-top: 3px solid #10B981;
    margin-bottom: 4px;
}
.building-card.warning  { border-top-color: #F59E0B; }
.building-card.high     { border-top-color: #EF4444; }
.building-card.critical { border-top-color: #7C3AED; }
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 28px 0 16px 0;
}
.section-icon {
    width: 36px; height: 36px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.tag-normal   { background:#ECFDF5; color:#059669; font-size:0.72rem; padding:2px 8px; border-radius:20px; font-weight:600; }
.tag-warning  { background:#FFFBEB; color:#D97706; font-size:0.72rem; padding:2px 8px; border-radius:20px; font-weight:600; }
.tag-critical { background:#FEF2F2; color:#DC2626; font-size:0.72rem; padding:2px 8px; border-radius:20px; font-weight:600; }
.delta-up   { color: #10B981; font-weight:600; font-size:0.78rem; }
.delta-down { color: #EF4444; font-weight:600; font-size:0.78rem; }
.metric-val { font-size: 2.0rem; font-weight: 800; color: #0F172A; line-height:1.1; }
.metric-sub { font-size: 0.78rem; color: #94A3B8; margin-top: 2px; }
.navbar {
    background: white;
    padding: 12px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #F1F5F9;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    margin-bottom: 0;
}
.equip-card {
    background: white; border-radius: 12px; padding: 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05); text-align: center;
}

/* Remove streamlit default padding */
div[data-testid="stVerticalBlock"] > div { gap: 0.5rem !important; }
.stPlotlyChart { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Director"

# ── Imports ───────────────────────────────────────────────────────────────────
from ui.dashboard import render_dashboard
from ui.dataset_explorer import render_dataset_explorer
from ui.analytics import render_analytics
from ui.simulator import render_simulator
from ui.load_optimization import render_load_optimization
from ui.recommendations import render_recommendations
from ui.alerts import render_alerts
from ui.reports import render_reports
from ui.settings import render_settings

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 8px 0; text-align:center;">
        <div style="display:inline-flex;align-items:center;justify-content:center;
                    background:linear-gradient(135deg,#3B82F6,#2563EB);
                    width:44px;height:44px;border-radius:12px;font-size:1.3rem;margin-bottom:8px;">
            ⚡
        </div>
        <div style="color:#F1F5F9;font-weight:700;font-size:1.05rem;">MIET</div>
        <div style="color:#64748B;font-size:0.72rem;letter-spacing:0.5px;text-transform:uppercase;">
            Smart Campus Energy
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #334155;margin:8px 0 16px 0;">
    """, unsafe_allow_html=True)

    selected_role = st.selectbox(
        "Active Profile",
        options=["Director", "Energy Manager", "Electrical Engineer", "Administrator"],
        index=["Director", "Energy Manager", "Electrical Engineer", "Administrator"]
               .index(st.session_state["user_role"])
    )
    st.session_state["user_role"] = selected_role

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    selected_page = st.radio(
        "Navigation",
        options=[
            "🏛️ Director Decision Centre",
            "⚡ Energy Analytics",
            "🔮 Scenario Simulator",
            "🔌 Load Optimization",
            "💡 AI Recommendations",
            "🔔 Smart Alerts",
            "🔍 Telemetry Explorer",
            "📄 Executive Report",
            "⚙️ Settings",
        ],
        label_visibility="collapsed"
    )

    st.markdown("""
    <hr style="border:none;border-top:1px solid #334155;margin:16px 0 8px 0;">
    <div style="color:#475569;font-size:0.72rem;text-align:center;">
        v1.0.0 · MIET Campus DSS
    </div>
    """, unsafe_allow_html=True)

# ── Navbar ────────────────────────────────────────────────────────────────────
from datetime import datetime
now = datetime.now().strftime("%I:%M:%S %p  %A, %d %b %Y")

st.markdown(f"""
<div class="navbar">
    <div style="display:flex;align-items:center;gap:14px;">
        <div style="background:linear-gradient(135deg,#3B82F6,#2563EB);
                    width:40px;height:40px;border-radius:10px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:1.2rem;">⚡</div>
        <div>
            <div style="font-weight:700;color:#0F172A;font-size:0.95rem;">MIET</div>
            <div style="color:#3B82F6;font-size:0.78rem;font-weight:500;">
                Smart Campus Energy Management System
            </div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:16px;">
        <span style="color:#475569;font-size:0.82rem;font-weight:500;">{now}</span>
        <span style="background:#F1F5F9;color:#475569;padding:4px 12px;
                     border-radius:20px;font-size:0.78rem;font-weight:600;">
            🌙 Night Mode
        </span>
        <span style="background:#ECFDF5;color:#059669;padding:4px 12px;
                     border-radius:20px;font-size:0.78rem;font-weight:600;
                     border:1px solid #D1FAE5;">
            ● Campus: Normal
        </span>
        <span style="background:#EFF6FF;color:#3B82F6;padding:4px 12px;
                     border-radius:20px;font-size:0.78rem;font-weight:600;
                     border:1px solid #DBEAFE;">
            Phase 1 · Live Monitoring
        </span>
    </div>
</div>
<div style="background:#F0F4F8;padding:0 28px 28px 28px;">
""", unsafe_allow_html=True)

# ── Router ────────────────────────────────────────────────────────────────────
try:
    if selected_page == "🏛️ Director Decision Centre":
        render_dashboard()
    elif selected_page == "⚡ Energy Analytics":
        render_analytics()
    elif selected_page == "🔮 Scenario Simulator":
        render_simulator()
    elif selected_page == "🔌 Load Optimization":
        render_load_optimization()
    elif selected_page == "💡 AI Recommendations":
        render_recommendations()
    elif selected_page == "🔔 Smart Alerts":
        render_alerts()
    elif selected_page == "🔍 Telemetry Explorer":
        render_dataset_explorer()
    elif selected_page == "📄 Executive Report":
        render_reports()
    elif selected_page == "⚙️ Settings":
        render_settings()
except Exception as e:
    st.error(f"🛑 Application Error: {e}")
    st.exception(e)

st.markdown("</div>", unsafe_allow_html=True)
