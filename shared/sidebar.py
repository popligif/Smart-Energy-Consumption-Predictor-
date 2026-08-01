"""
Shared sidebar renderer — renders once, same structure on all pages.
"""
import streamlit as st
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

ALL_PAGES_META = {
    "🏛️ Executive Decision Centre": {"cat": "Overview",    "desc": "KPIs & campus health"},
    "🏢 Building Drill-Down":        {"cat": "Overview",    "desc": "Per-building analysis"},
    "⚡ Energy Analytics":            {"cat": "Analytics",   "desc": "Trends & comparisons"},
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
        "🔮 Scenario Simulator",
        "🔌 Load Optimization",
        "🔍 Telemetry Explorer",
        "⚙️ Settings",
        "🗺️ System Guide",
    ],
    "Administrator": list(ALL_PAGES_META.keys()),
}

CAT_COLORS = {
    "Overview":    "#3B82F6",
    "Analytics":   "#8B5CF6",
    "Management":  "#F59E0B",
    "System":      "#64748B",
}


def render_sidebar() -> str:
    """
    Renders the full sidebar. Returns the selected page name.
    """
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = "Director"

    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────
        st.markdown("""
<div style="padding:20px 12px 14px 12px;text-align:center;">
    <div style="display:inline-flex;align-items:center;justify-content:center;
                background:linear-gradient(135deg,#10B981,#059669);
                width:52px;height:52px;border-radius:16px;font-size:1.5rem;
                margin-bottom:10px;box-shadow:0 6px 20px rgba(16,185,129,0.45);">
        ⚡
    </div>
    <div style="color:#F1F5F9;font-weight:800;font-size:1.05rem;letter-spacing:0.3px;line-height:1.2;">
        MIET Campus
    </div>
    <div style="color:#475569;font-size:0.68rem;letter-spacing:1.2px;
                text-transform:uppercase;margin-top:2px;">
        Energy Intelligence
    </div>
</div>
<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0 0 12px 0;">
""", unsafe_allow_html=True)

        # ── Role selector ─────────────────────────────────────────────
        st.markdown("""
<div style="padding:0 4px;margin-bottom:6px;">
    <span style="color:#475569;font-size:0.7rem;font-weight:600;
                 letter-spacing:0.8px;text-transform:uppercase;">
        Active Profile
    </span>
</div>
""", unsafe_allow_html=True)

        selected_role = st.selectbox(
            "Active Profile",
            options=["Director", "Energy Manager", "Electrical Engineer", "Administrator"],
            index=["Director", "Energy Manager", "Electrical Engineer", "Administrator"]
                   .index(st.session_state["user_role"]),
            key="role_select",
            label_visibility="collapsed"
        )
        st.session_state["user_role"] = selected_role

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # ── Navigation ────────────────────────────────────────────────
        visible_pages = ROLE_PAGES.get(selected_role, list(ALL_PAGES_META.keys()))

        # Group pages by category
        categories = {}
        for page in visible_pages:
            cat = ALL_PAGES_META[page]["cat"]
            categories.setdefault(cat, []).append(page)

        # Render grouped nav with category headers
        for cat, pages in categories.items():
            color = CAT_COLORS.get(cat, "#64748B")
            st.markdown(f"""
<div style="padding:6px 10px 4px 10px;">
    <span style="color:{color};font-size:0.68rem;font-weight:700;
                 letter-spacing:1px;text-transform:uppercase;">
        {cat}
    </span>
</div>
""", unsafe_allow_html=True)
            for page in pages:
                pass  # placeholder — actual radio below

        # Single radio for all visible pages (st.navigation handles this)
        selected_page = st.radio(
            "Navigation",
            options=visible_pages,
            label_visibility="collapsed",
            key="nav_radio"
        )

        # ── Footer ────────────────────────────────────────────────────
        now_str = datetime.now(IST).strftime("%H:%M · %d %b")
        st.markdown(f"""
<hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:14px 0 8px 0;">
<div style="padding:0 8px 12px 8px;">
    <div style="color:#334155;font-size:0.7rem;font-weight:500;margin-bottom:4px;">
        🕐 {now_str} IST
    </div>
    <div style="display:flex;align-items:center;gap:6px;">
        <div style="width:6px;height:6px;border-radius:50%;background:#10B981;
                    box-shadow:0 0 6px #10B981;animation:pulse 2s infinite;"></div>
        <span style="color:#334155;font-size:0.7rem;">System Online · v1.0.0</span>
    </div>
</div>
<style>
@keyframes pulse {{
    0%,100% {{ opacity:1; transform:scale(1); }}
    50%      {{ opacity:0.5; transform:scale(1.4); }}
}}
</style>
""", unsafe_allow_html=True)

    return selected_page
