"""
Shared top navbar — rendered once per page as a single st.markdown call.
"""
import streamlit as st
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

PAGE_DESCRIPTIONS = {
    "🏛️ Executive Decision Centre": "Real-time campus KPIs, building status, and executive insights",
    "🏢 Building Drill-Down":        "Per-building energy breakdown, equipment analysis, and trends",
    "⚡ Energy Analytics":            "Hourly trends, building comparisons, peak demand analysis",
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


def render_navbar(selected_page: str):
    """Renders the sticky top navbar with page title and live status."""
    now = datetime.now(IST).strftime("%I:%M %p · %a, %d %b %Y")
    desc = PAGE_DESCRIPTIONS.get(selected_page, "")
    accent = ACCENT_COLORS.get(selected_page, "#10B981")
    role = st.session_state.get("user_role", "Director")

    role_colors = {
        "Director": "#3B82F6",
        "Energy Manager": "#10B981",
        "Electrical Engineer": "#F59E0B",
        "Administrator": "#8B5CF6",
    }
    role_color = role_colors.get(role, "#64748B")

    st.markdown(f"""
<div style="
    background: white;
    padding: 12px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid {accent}18;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin: -2rem -2rem 24px -2rem;
    position: sticky;
    top: 0;
    z-index: 999;
    backdrop-filter: blur(12px);
">
    <div style="display:flex;align-items:center;gap:14px;">
        <div style="
            background: linear-gradient(135deg,{accent},{accent}CC);
            width: 42px; height: 42px;
            border-radius: 12px;
            display: flex; align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            box-shadow: 0 4px 12px {accent}40;
            flex-shrink: 0;
        ">⚡</div>
        <div>
            <div style="font-weight:800;color:#0F172A;font-size:1rem;letter-spacing:-0.01em;">
                {selected_page}
            </div>
            <div style="color:#64748B;font-size:0.76rem;font-weight:400;margin-top:1px;">
                {desc}
            </div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
        <span style="color:#94A3B8;font-size:0.76rem;font-weight:500;
                     font-variant-numeric:tabular-nums;">
            🕐 {now}
        </span>
        <span style="background:{role_color}15;color:{role_color};
                     padding:4px 12px;border-radius:20px;
                     font-size:0.72rem;font-weight:700;
                     border:1px solid {role_color}30;">
            {role}
        </span>
        <span style="background:#ECFDF5;color:#10B981;
                     padding:4px 12px;border-radius:20px;
                     font-size:0.72rem;font-weight:700;
                     border:1px solid #A7F3D0;">
            ● Live
        </span>
    </div>
</div>
""", unsafe_allow_html=True)
