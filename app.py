"""
Main application router and entry point.
MIET Smart Campus Energy Intelligence & Decision Support System
"""
import streamlit as st
from datetime import datetime, timezone, timedelta
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

# ── Global CSS Design System ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* Page background */
.main .block-container {
    padding-top: 0 !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
    background: #F0F4F8;
}
.main { background-color: #F0F4F8 !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
    border-right: 1px solid #334155 !important;
}
section[data-testid="stSidebar"] > div { background: transparent !important; }
section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label { color: #94A3B8 !important; }

/* Card styles used across all pages */
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.04);
    border: 1px solid #F1F5F9;
    height: 100%;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.09);
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
.equip-card {
    background: white;
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    text-align: center;
}
.delta-up   { color: #10B981; font-weight: 600; font-size: 0.78rem; }
.delta-down { color: #EF4444; font-weight: 600; font-size: 0.78rem; }
.metric-val { font-size: 2.0rem; font-weight: 800; color: #0F172A; line-height: 1.1; }
.metric-sub { font-size: 0.78rem; color: #94A3B8; margin-top: 2px; }

/* Remove extra gaps */
div[data-testid="stVerticalBlock"] > div { gap: 0.5rem !important; }
div[data-testid="stHorizontalBlock"] { gap: 1rem !important; }
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
from ui.future_works import render_future_works

# ── Role-Based Page Access ────────────────────────────────────────────────────
ALL_PAGES = [
    "🏛️ Executive Decision Centre",
    "⚡ Energy Analytics",
    "🔮 Scenario Simulator",
    "🔌 Load Optimization",
    "💡 AI Recommendations",
    "🔔 Smart Alerts",
    "🔍 Telemetry Explorer",
    "📄 Executive Report",
    "⚙️ Settings",
    "🔮 Future Integrations",
]

ROLE_PAGES = {
    "Director": ALL_PAGES,
    "Energy Manager": ALL_PAGES,
    "Electrical Engineer": ALL_PAGES,
    "Administrator": ALL_PAGES,
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 8px 12px 8px;text-align:center;">
        <div style="display:inline-flex;align-items:center;justify-content:center;
                    background:linear-gradient(135deg,#3B82F6,#2563EB);
                    width:50px;height:50px;border-radius:14px;
                    font-size:1.4rem;margin-bottom:10px;box-shadow:0 4px 12px rgba(59,130,246,0.4);">
            ⚡
        </div>
        <div style="color:#F1F5F9;font-weight:800;font-size:1.1rem;letter-spacing:0.5px;">MIET</div>
        <div style="color:#64748B;font-size:0.7rem;letter-spacing:1px;text-transform:uppercase;">
            Smart Campus Energy
        </div>
    </div>
    <hr style="border:none;border-top:1px solid #334155;margin:0 0 14px 0;">
    """, unsafe_allow_html=True)

    selected_role = st.selectbox(
        "Active Profile",
        options=["Director", "Energy Manager", "Electrical Engineer", "Administrator"],
        index=["Director", "Energy Manager", "Electrical Engineer", "Administrator"]
               .index(st.session_state["user_role"]),
        key="role_select"
    )
    st.session_state["user_role"] = selected_role

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Show only pages allowed for the current role
    visible_pages = ROLE_PAGES.get(selected_role, ALL_PAGES)

    selected_page = st.radio(
        "Navigation",
        options=visible_pages,
        label_visibility="collapsed",
        key="nav_radio"
    )

    st.markdown("""
    <hr style="border:none;border-top:1px solid #334155;margin:14px 0 8px 0;">
    <div style="color:#475569;font-size:0.7rem;text-align:center;padding-bottom:8px;">
        v1.0.0 &nbsp;·&nbsp; MIET Campus DSS
    </div>
    """, unsafe_allow_html=True)

# ── Navbar (rendered OUTSIDE sidebar context, directly in main area) ──────────
# Use IST timezone (UTC+05:30) for correct time display
IST = timezone(timedelta(hours=5, minutes=30))
now = datetime.now(IST).strftime("%I:%M:%S %p  %A, %d %b %Y")

# Use a st.container so the navbar is guaranteed to be the first element in main
with st.container():
    st.markdown(f"""
    <div style="
        background: white;
        padding: 14px 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #F1F5F9;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        margin: -2rem -2rem 24px -2rem;
        position: sticky;
        top: 0;
        z-index: 999;
    ">
        <div style="display:flex;align-items:center;gap:14px;">
            <div style="
                background: linear-gradient(135deg,#3B82F6,#2563EB);
                width: 42px; height: 42px; border-radius: 12px;
                display: flex; align-items: center; justify-content: center;
                font-size: 1.3rem;
                box-shadow: 0 4px 10px rgba(59,130,246,0.35);
            ">⚡</div>
            <div>
                <div style="font-weight:800;color:#0F172A;font-size:1.0rem;
                             letter-spacing:0.3px;">MIET</div>
                <div style="color:#3B82F6;font-size:0.78rem;font-weight:600;">
                    Smart Campus Energy Management System
                </div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
            <span style="color:#64748B;font-size:0.8rem;font-weight:500;
                          font-variant-numeric:tabular-nums;">{now}</span>
            <span style="background:#F8FAFC;color:#64748B;padding:5px 14px;
                         border-radius:20px;font-size:0.75rem;font-weight:600;
                         border:1px solid #E2E8F0;">
                🌙 Night Mode
            </span>
            <span style="background:#ECFDF5;color:#059669;padding:5px 14px;
                         border-radius:20px;font-size:0.75rem;font-weight:700;
                         border:1px solid #A7F3D0;">
                ● Campus: Normal
            </span>
            <span style="background:#EFF6FF;color:#2563EB;padding:5px 14px;
                         border-radius:20px;font-size:0.75rem;font-weight:700;
                         border:1px solid #BFDBFE;">
                ⚡ Phase 1 · Live Monitoring
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Router ────────────────────────────────────────────────────────────────────
try:
    if selected_page == "🏛️ Executive Decision Centre":
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
    elif selected_page == "🔮 Future Integrations":
        render_future_works()
except Exception as e:
    st.error(f"🛑 Application Error: {e}")
    st.exception(e)
