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
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

/* Dynamic Background & Spacing */
.main .block-container {
    padding-top: 0 !important;
    padding-left: 2.5rem !important;
    padding-right: 2.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 100% !important;
    background: #F8FAFC;
    background-image: radial-gradient(#E2E8F0 1px, transparent 1px);
    background-size: 24px 24px;
}
.main { background-color: #F8FAFC !important; }

/* Premium Glassmorphic Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #022C22 0%, #064E3B 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
    box-shadow: 4px 0 24px rgba(2, 44, 34, 0.4);
}
section[data-testid="stSidebar"] > div { background: transparent !important; }
section[data-testid="stSidebar"] * { color: #A7F3D0 !important; }
section[data-testid="stSidebar"] hr { border-top-color: rgba(167, 243, 208, 0.2) !important; }

/* Sidebar Navigation Radios styled as pills */
section[data-testid="stSidebar"] .stRadio > div { gap: 4px; }
section[data-testid="stSidebar"] .stRadio label {
    background: rgba(255,255,255,0.03);
    padding: 10px 16px;
    border-radius: 12px;
    transition: all 0.2s ease;
    cursor: pointer;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(16, 185, 129, 0.15);
    transform: translateX(4px);
}
section[data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p {
    font-size: 0.95rem; font-weight: 500; color: #D1FAE5 !important;
}

/* Stunning KPI Cards with Micro-animations */
.kpi-card {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    border: 1px solid rgba(226, 232, 240, 0.8);
    height: 100%;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #10B981, #059669);
    opacity: 0; transition: opacity 0.3s ease;
}
.kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 25px -5px rgba(5, 150, 105, 0.1), 0 10px 10px -5px rgba(5, 150, 105, 0.04);
}
.kpi-card:hover::before { opacity: 1; }

.building-card {
    background: white;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    border: 1px solid #F1F5F9;
    border-left: 4px solid #10B981;
    margin-bottom: 8px;
    transition: transform 0.2s;
}
.building-card:hover { transform: scale(1.01); }

.equip-card {
    background: linear-gradient(135deg, #ffffff, #f8fafc);
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    border: 1px solid #e2e8f0;
    text-align: center;
}

/* Typography Enhancements */
.delta-up   { color: #10B981; font-weight: 700; font-size: 0.85rem; background: #ECFDF5; padding: 2px 8px; border-radius: 12px; }
.delta-down { color: #EF4444; font-weight: 700; font-size: 0.85rem; background: #FEF2F2; padding: 2px 8px; border-radius: 12px; }
.metric-val { font-size: 2.4rem; font-weight: 800; color: #022C22; line-height: 1.1; letter-spacing: -0.02em; }
.metric-sub { font-size: 0.85rem; color: #64748B; margin-top: 4px; font-weight: 500; }

/* Fix Streamlit defaults */
button[title="View fullscreen"] { display: none; }
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
from ui.building_drilldown import render_building_drilldown

# ── Role-Based Page Access ────────────────────────────────────────────────────
ALL_PAGES = [
    "🏛️ Executive Decision Centre",
    "🏢 Building Drill-Down",
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
    "Director": [
        "🏛️ Executive Decision Centre",
        "🏢 Building Drill-Down",
        "⚡ Energy Analytics",
        "💡 AI Recommendations",
        "🔔 Smart Alerts",
        "📄 Executive Report",
        "⚙️ Settings",
    ],
    "Energy Manager": [
        "🏛️ Executive Decision Centre",
        "🏢 Building Drill-Down",
        "⚡ Energy Analytics",
        "🔮 Scenario Simulator",
        "🔌 Load Optimization",
        "💡 AI Recommendations",
        "🔔 Smart Alerts",
        "📄 Executive Report",
        "⚙️ Settings",
    ],
    "Electrical Engineer": [
        "🏛️ Executive Decision Centre",
        "🏢 Building Drill-Down",
        "⚡ Energy Analytics",
        "🔮 Scenario Simulator",
        "🔌 Load Optimization",
        "🔍 Telemetry Explorer",
        "⚙️ Settings",
    ],
    "Administrator": ALL_PAGES,
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:20px 8px 12px 8px;text-align:center;">
        <div style="display:inline-flex;align-items:center;justify-content:center;
                    background:linear-gradient(135deg,#059669,#047857);
                    width:50px;height:50px;border-radius:14px;
                    font-size:1.4rem;margin-bottom:10px;box-shadow:0 4px 12px rgba(5,150,105,0.4);">
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
                background: linear-gradient(135deg,#059669,#047857);
                width: 42px; height: 42px; border-radius: 12px;
                display: flex; align-items: center; justify-content: center;
                font-size: 1.3rem;
                box-shadow: 0 4px 10px rgba(5,150,105,0.35);
            ">⚡</div>
            <div>
                <div style="font-weight:800;color:#0F172A;font-size:1.0rem;
                             letter-spacing:0.3px;">MIET</div>
                <div style="color:#059669;font-size:0.78rem;font-weight:600;">
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
            <span style="background:#ECFDF5;color:#047857;padding:5px 14px;
                         border-radius:20px;font-size:0.75rem;font-weight:700;
                         border:1px solid #A7F3D0;">
                ⚡ Phase 1 · Live Monitoring
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Router ────────────────────────────────────────────────────────────────────
try:
    if selected_page == "🏛️ Executive Decision Centre":
        render_dashboard()
    elif selected_page == "🏢 Building Drill-Down":
        render_building_drilldown()
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
