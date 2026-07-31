"""
MIET Smart Campus Energy Intelligence & Decision Support System
Main entry point — uses st.navigation for smooth, flash-free page transitions.
"""
import streamlit as st
from config.logging import setup_logging
from config.settings import ConfigSettings

setup_logging()
ConfigSettings()  # initialise once at startup

st.set_page_config(
    page_title="MIET Smart Campus Energy Management",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS once per session (not every rerun) ─────────────────────────────
from shared.styles import inject_styles
inject_styles()

# ── Session defaults ──────────────────────────────────────────────────────────
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Director"

# ── Render sidebar & get selected page ───────────────────────────────────────
from shared.sidebar import render_sidebar
selected_page = render_sidebar()

# ── Render navbar ─────────────────────────────────────────────────────────────
from shared.navbar import render_navbar
render_navbar(selected_page)

# ── Page imports (lazy — only the needed page runs its logic) ─────────────────
try:
    if selected_page == "🏛️ Executive Decision Centre":
        from ui.dashboard import render_dashboard
        render_dashboard()

    elif selected_page == "🏢 Building Drill-Down":
        from ui.building_drilldown import render_building_drilldown
        render_building_drilldown()

    elif selected_page == "⚡ Energy Analytics":
        from ui.analytics import render_analytics
        render_analytics()

    elif selected_page == "🔮 Scenario Simulator":
        from ui.simulator import render_simulator
        render_simulator()

    elif selected_page == "🔌 Load Optimization":
        from ui.load_optimization import render_load_optimization
        render_load_optimization()

    elif selected_page == "💡 AI Recommendations":
        from ui.recommendations import render_recommendations
        render_recommendations()

    elif selected_page == "🔔 Smart Alerts":
        from ui.alerts import render_alerts
        render_alerts()

    elif selected_page == "🔍 Telemetry Explorer":
        from ui.dataset_explorer import render_dataset_explorer
        render_dataset_explorer()

    elif selected_page == "📄 Executive Report":
        from ui.reports import render_reports
        render_reports()

    elif selected_page == "⚙️ Settings":
        from ui.settings import render_settings
        render_settings()

    elif selected_page == "🔮 Future Integrations":
        from ui.future_works import render_future_works
        render_future_works()

    elif selected_page == "🗺️ System Guide":
        from ui.guide import render_guide
        render_guide()

except Exception as e:
    st.error(f"⚠️ Page rendering error on **{selected_page}**: {e}")
    st.exception(e)
