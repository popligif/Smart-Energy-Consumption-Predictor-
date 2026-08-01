"""
Shared sidebar renderer — grouped navigation with categories.
"""
import streamlit as st
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

ALL_PAGES_META = {
    "🏛️ Executive Decision Centre": {"cat": "Overview",    "desc": "KPIs & campus health"},
    "🏢 Building Drill-Down":        {"cat": "Overview",    "desc": "Per-building analysis"},
    "⚡ Energy Analytics":            {"cat": "Analytics",   "desc": "Trends & comparisons"},
    "📈 Energy Forecasting":          {"cat": "Analytics",   "desc": "ML predictions"},
    "🔍 Telemetry Explorer":          {"cat": "Analytics",   "desc": "Raw data & exports"},
    "🔮 Scenario Simulator":          {"cat": "Management",  "desc": "What-if projections"},
    "🔌 Load Optimization":           {"cat": "Management",  "desc": "Load balancing"},
    "💡 AI Recommendations":          {"cat": "Management",  "desc": "AI-driven actions"},
    "🔔 Smart Alerts":                {"cat": "Management",  "desc": "Threshold alerts"},
    "📄 Executive Report":            {"cat": "System",      "desc": "PDF summaries"},
    "⚙️ Settings":                    {"cat": "System",      "desc": "Preferences"},
    "🔮 Future Integrations":         {"cat": "System",      "desc": "Roadmap"},
    "🗺️ System Guide":               {"cat": "System",      "desc": "Site map & help"},
}

ROLE_PAGES = {
    "Director": [
        "🏛️ Executive Decision Centre",
        "🏢 Building Drill-Down",
        "⚡ Energy Analytics",
        "📈 Energy Forecasting",
        "💡 AI Recommendations",
        "🔔 Smart Alerts",
        "📄 Executive Report",
        "⚙️ Settings",
        "🗺️ System Guide",
    ],
    "Energy Manager": [
        "🏛️ Executive Decision Centre",
        "🏢 Building Drill-Down",
        "⚡ Energy Analytics",
        "📈 Energy Forecasting",
        "🔮 Scenario Simulator",
        "🔌 Load Optimization",
        "💡 AI Recommendations",
        "🔔 Smart Alerts",
        "📄 Executive Report",
        "⚙️ Settings",
        "🗺️ System Guide",
    ],
    "Electrical Engineer": [
        "🏛️ Executive Decision Centre",
        "🏢 Building Drill-Down",
        "⚡ Energy Analytics",
        "📈 Energy Forecasting",
        "🔮 Scenario Simulator",
        "🔌 Load Optimization",
        "🔍 Telemetry Explorer",
        "⚙️ Settings",
        "🗺️ System Guide",
    ],
    "Administrator": list(ALL_PAGES_META.keys()),
}

CAT_COLORS = {
    "Overview":   "#3B82F6",
    "Analytics":  "#8B5CF6",
    "Management": "#F59E0B",
    "System":     "#64748B",
}


def render_sidebar() -> str:
    """Renders the full sidebar. Returns the selected page name."""
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = "Director"

    with st.sidebar:
        # ── Logo ──
        st.markdown("""
<div style="padding:22px 12px 16px 12px;text-align:center;">
    <div style="display:inline-flex;align-items:center;justify-content:center;
                background:linear-gradient(135deg,#10B981 0%,#059669 100%);
                width:54px;height:54px;border-radius:16px;font-size:1.6rem;
                margin-bottom:12px;
                box-shadow:0 8px 24px rgba(16,185,129,0.5),0 0 0 4px rgba(16,185,129,0.15);">
        ⚡
    </div>
    <div style="color:#F1F5F9;font-weight:800;font-size:1.1rem;
                letter-spacing:0.3px;line-height:1.2;">
        MIET Campus
    </div>
    <div style="color:#A7F3D0;font-size:0.65rem;letter-spacing:1.5px;
                text-transform:uppercase;margin-top:3px;font-weight:600;">
        Energy Intelligence System
    </div>
</div>
<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:0 0 14px 0;">
""", unsafe_allow_html=True)

        # ── Role selector ──
        selected_role = st.selectbox(
            "Active Profile",
            options=["Director", "Energy Manager", "Electrical Engineer", "Administrator"],
            index=["Director", "Energy Manager", "Electrical Engineer", "Administrator"]
                   .index(st.session_state["user_role"]),
            key="role_select",
        )
        st.session_state["user_role"] = selected_role

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # ── Navigation ──
        visible_pages = ROLE_PAGES.get(selected_role, list(ALL_PAGES_META.keys()))

        # Build grouped category headers HTML (visual only)
        cats_seen = []
        cat_html_parts = []
        for page in visible_pages:
            cat = ALL_PAGES_META[page]["cat"]
            if cat not in cats_seen:
                cats_seen.append(cat)
        for cat in cats_seen:
            color = CAT_COLORS.get(cat, "#64748B")
            cat_html_parts.append(
                f'<span style="display:inline-block;background:{color}18;color:{color};'
                f'padding:3px 10px;border-radius:8px;font-size:0.65rem;font-weight:700;'
                f'letter-spacing:0.8px;text-transform:uppercase;margin:2px 2px;">{cat}</span>'
            )

        st.markdown(
            '<div style="display:flex;flex-wrap:wrap;gap:4px;padding:0 8px;margin-bottom:8px;">'
            + "".join(cat_html_parts)
            + "</div>",
            unsafe_allow_html=True,
        )

        # Single radio
        selected_page = st.radio(
            "Navigation",
            options=visible_pages,
            label_visibility="collapsed",
            key="nav_radio",
        )

        # ── Footer ──
        now_str = datetime.now(IST).strftime("%H:%M · %d %b %Y")
        st.markdown(f"""
<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:14px 0 8px 0;">
<div style="padding:4px 10px 14px 10px;">
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">
        <div style="width:7px;height:7px;border-radius:50%;background:#10B981;
                    box-shadow:0 0 8px #10B981,0 0 16px rgba(16,185,129,0.3);
                    animation:pulseGlow 2s ease-in-out infinite;"></div>
        <span style="color:#E2E8F0;font-size:0.7rem;font-weight:500;">System Online</span>
    </div>
    <div style="color:#CBD5E1;font-size:0.68rem;font-weight:400;">
        {now_str} IST · v1.0.0
    </div>
</div>
<style>
@keyframes pulseGlow {{
    0%,100% {{ opacity:1; box-shadow:0 0 8px #10B981,0 0 16px rgba(16,185,129,0.3); }}
    50%     {{ opacity:0.6; box-shadow:0 0 4px #10B981,0 0 8px rgba(16,185,129,0.1); }}
}}
</style>
""", unsafe_allow_html=True)

    return selected_page
