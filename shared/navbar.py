"""
Shared top navbar — rendered once per page as a single st.markdown call.
Dynamically shows page emoji, title, description, role badge, and accent line.
"""
import streamlit as st
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

PAGE_DESCRIPTIONS = {
    "🏛️ Executive Decision Centre": "Real-time campus KPIs, building status, and executive insights",
    "🏢 Building Drill-Down":        "Per-building energy breakdown, equipment analysis, and trends",
    "⚡ Energy Analytics":            "Hourly trends, building comparisons, peak demand analysis",
    "📈 Energy Forecasting":          "ML-powered next hour, day, week & month predictions",
    "🔍 Telemetry Explorer":          "Raw sensor data, filtering, export, and data quality checks",
    "🔮 Scenario Simulator":          "Model what-if scenarios and project energy & cost outcomes",
    "🔌 Load Optimization":           "Load balancing recommendations and shift opportunities",
    "💡 AI Recommendations":          "AI-generated action items ranked by impact and feasibility",
    "🔔 Smart Alerts":                "Threshold breach alerts, anomaly detection, and escalations",
    "📄 Executive Report":            "Automated PDF reports for management and board review",
    "⚙️ Settings":                    "Configure tariffs, thresholds, and system preferences",
    "🔮 Future Integrations":         "Planned IoT, ML, and API integrations roadmap",
    "🗺️ System Guide":               "Interactive site map showing all pages and their features",
}

ACCENT_COLORS = {
    "🏛️ Executive Decision Centre": "#10B981",
    "🏢 Building Drill-Down":        "#3B82F6",
    "⚡ Energy Analytics":            "#8B5CF6",
    "📈 Energy Forecasting":          "#06B6D4",
    "🔍 Telemetry Explorer":          "#06B6D4",
    "🔮 Scenario Simulator":          "#F59E0B",
    "🔌 Load Optimization":           "#EF4444",
    "💡 AI Recommendations":          "#10B981",
    "🔔 Smart Alerts":                "#EF4444",
    "📄 Executive Report":            "#64748B",
    "⚙️ Settings":                    "#64748B",
    "🔮 Future Integrations":         "#8B5CF6",
    "🗺️ System Guide":               "#3B82F6",
}


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert hex color to rgba string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


ROLE_STYLES = {
    "Director":            ("#3B82F6", "rgba(59,130,246,0.12)"),
    "Energy Manager":      ("#10B981", "rgba(16,185,129,0.12)"),
    "Electrical Engineer": ("#F59E0B", "rgba(245,158,11,0.12)"),
    "Administrator":       ("#8B5CF6", "rgba(139,92,246,0.12)"),
}


def render_navbar(selected_page: str):
    """Renders the sticky top navbar with page title and live status."""
    now  = datetime.now(IST).strftime("%I:%M %p · %a, %d %b %Y")
    desc = PAGE_DESCRIPTIONS.get(selected_page, "MIET Smart Campus EMS")
    accent = ACCENT_COLORS.get(selected_page, "#10B981")
    role = st.session_state.get("user_role", "Director")

    role_color, role_bg = ROLE_STYLES.get(role, ("#64748B", "rgba(100,116,139,0.12)"))
    icon_bg   = _hex_to_rgba(accent, 0.12)
    icon_glow = _hex_to_rgba(accent, 0.25)

    # Extract the leading emoji from page name
    page_emoji = selected_page.split(" ")[0] if selected_page else "⚡"
    # Clean display title (remove emoji prefix)
    display_title = " ".join(selected_page.split(" ")[1:]) if " " in selected_page else selected_page

    st.markdown(f"""
<div style="
    background: white;
    padding: 14px 28px 16px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    margin: -2rem -2rem 24px -2rem;
    position: sticky; top: 0; z-index: 999;
    border-bottom: 2px solid {accent};
">
    <div style="display:flex;align-items:center;gap:16px;">
        <div style="
            width: 48px; height: 48px;
            border-radius: 14px;
            background: {icon_bg};
            border: 1px solid {icon_glow};
            display: flex; align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            flex-shrink: 0;
        ">{page_emoji}</div>
        <div>
            <div style="font-weight:800;color:#0F172A;font-size:1.15rem;
                        letter-spacing:-0.02em;line-height:1.2;">
                {display_title}
            </div>
            <div style="color:#64748B;font-size:0.78rem;font-weight:400;margin-top:2px;">
                {desc}
            </div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
        <span style="color:#94A3B8;font-size:0.76rem;font-weight:500;
                     font-variant-numeric:tabular-nums;">
            🕐 {now}
        </span>
        <span style="background:{role_bg};color:{role_color};
                     padding:4px 12px;border-radius:20px;
                     font-size:0.72rem;font-weight:700;
                     border:1px solid {_hex_to_rgba(role_color, 0.25)};">
            {role}
        </span>
        <span style="background:rgba(16,185,129,0.1);color:#10B981;
                     padding:4px 12px;border-radius:20px;
                     font-size:0.72rem;font-weight:700;
                     border:1px solid rgba(16,185,129,0.25);">
            ● Live
        </span>
    </div>
</div>
""", unsafe_allow_html=True)
