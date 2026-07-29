"""
Main application router and entry point for the MIET Smart Campus Energy Command Centre.
"""
import streamlit as st
from config.logging import setup_logging
from config.settings import ConfigSettings

# Setup systems
setup_logging()
settings_manager = ConfigSettings()

# Page configurations
st.set_page_config(
    page_title="MIET Campus Energy Command Centre",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State variables
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Director"

# Import UI layers
from ui.dashboard import render_dashboard
from ui.dataset_explorer import render_dataset_explorer
from ui.analytics import render_analytics
from ui.simulator import render_simulator
from ui.load_optimization import render_load_optimization
from ui.recommendations import render_recommendations
from ui.alerts import render_alerts
from ui.reports import render_reports
from ui.settings import render_settings

# Sidebar Navigation Panel
st.sidebar.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #1A365D; margin-bottom: 0;">⚡ MIET</h2>
        <span style="font-size: 0.85rem; color: #4A5568; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">Energy Command Centre</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# User Session Persona selector (Role-Based Access)
st.sidebar.subheader("Select User Profile")
selected_role = st.sidebar.selectbox(
    "Active Persona Profile",
    options=["Director", "Energy Manager", "Electrical Engineer", "Administrator"],
    index=["Director", "Energy Manager", "Electrical Engineer", "Administrator"].index(st.session_state["user_role"])
)
st.session_state["user_role"] = selected_role

st.sidebar.markdown("---")

# Filter Navigation options based on user role (NFR-5 / Role Mapping)
st.sidebar.subheader("Navigation Menu")

role_nav_map = {
    "Director": ["🏛️ Director Decision Centre", "💡 AI Recommendations", "📄 Executive PDF Reports"],
    "Energy Manager": ["🏛️ Director Decision Centre", "⚡ Energy Command Centre", "🔮 Scenario Simulator", "🔌 Load Optimization", "🔔 Operational Alerts"],
    "Electrical Engineer": ["⚡ Energy Command Centre", "🔮 Scenario Simulator", "🔔 Operational Alerts", "🔍 Telemetry Explorer"],
    "Administrator": ["🏛️ Director Decision Centre", "⚙️ Calibration Settings"]
}

# For a flexible design, we allow the active role to filter the defaults, but allow viewing all sections under an 'All Modules' toggle
show_all_modules = st.sidebar.checkbox("Expose All Modules (Developer Mode)", value=True)

if show_all_modules:
    nav_options = [
        "🏛️ Director Decision Centre",
        "🔍 Telemetry Explorer",
        "⚡ Energy Command Centre",
        "🔮 Scenario Simulator",
        "🔌 Load Optimization",
        "💡 AI Recommendations",
        "🔔 Operational Alerts",
        "📄 Executive PDF Reports",
        "⚙️ Calibration Settings"
    ]
else:
    # Use mapped options
    mapped = role_nav_map.get(selected_role, ["🏛️ Director Decision Centre"])
    # Map friendly names for presentation
    nav_options = []
    if "🏛️ Director Decision Centre" in mapped: nav_options.append("🏛️ Director Decision Centre")
    if "🔍 Telemetry Explorer" in mapped or "🔍 Telemetry Explorer" in mapped: nav_options.append("🔍 Telemetry Explorer")
    if "⚡ Energy Command Centre" in mapped: nav_options.append("⚡ Energy Command Centre")
    if "🔮 Scenario Simulator" in mapped: nav_options.append("🔮 Scenario Simulator")
    if "🔌 Load Optimization" in mapped: nav_options.append("🔌 Load Optimization")
    if "💡 AI Recommendations" in mapped: nav_options.append("💡 AI Recommendations")
    if "🔔 Operational Alerts" in mapped: nav_options.append("🔔 Operational Alerts")
    if "📄 Executive PDF Reports" in mapped: nav_options.append("📄 Executive PDF Reports")
    if "⚙️ Calibration Settings" in mapped or "⚙️ Calibration Settings" in mapped: nav_options.append("⚙️ Calibration Settings")

selected_page = st.sidebar.radio(
    "Go To Section:",
    options=nav_options
)

# Route to corresponding pages
try:
    if selected_page == "🏛️ Director Decision Centre":
        render_dashboard()
    elif selected_page == "🔍 Telemetry Explorer":
        render_dataset_explorer()
    elif selected_page == "⚡ Energy Command Centre":
        render_analytics()
    elif selected_page == "🔮 Scenario Simulator":
        render_simulator()
    elif selected_page == "🔌 Load Optimization":
        render_load_optimization()
    elif selected_page == "💡 AI Recommendations":
        render_recommendations()
    elif selected_page == "🔔 Operational Alerts":
        render_alerts()
    elif selected_page == "📄 Executive PDF Reports":
        render_reports()
    elif selected_page == "⚙️ Calibration Settings":
        render_settings()
except Exception as e:
    st.error(f"🛑 Critical System Routing Error: {e}")
    st.exception(e)
