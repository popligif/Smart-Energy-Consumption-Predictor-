"""
System Guide — Interactive site map showing all pages, features, and role access.
"""
import streamlit as st


def render_guide():
    """Renders the interactive system flow map / site guide."""

    # ── Category definitions ──────────────────────────────────────────────────
    categories = [
        {
            "name": "Overview",
            "icon": "📊",
            "color": "#3B82F6",
            "bg": "#EFF6FF",
            "border": "#BFDBFE",
            "pages": [
                {
                    "icon": "🏛️",
                    "name": "Executive Decision Centre",
                    "key": "🏛️ Executive Decision Centre",
                    "features": [
                        "Real-time KPI cards (energy, cost, carbon, power factor)",
                        "Campus-wide equipment status (ACs, PCs, lighting)",
                        "Hourly consumption trend with peak/off-peak zones",
                        "Building-wise power breakdown chart",
                        "Feature importance (what drives consumption)",
                        "Active alert count & severity summary",
                    ]
                },
                {
                    "icon": "🏢",
                    "name": "Building Drill-Down",
                    "key": "🏢 Building Drill-Down",
                    "features": [
                        "Select any building for deep-dive analysis",
                        "Hourly energy trend for selected building",
                        "Equipment utilization (ACs, PCs, lighting, HVAC)",
                        "Occupancy vs consumption correlation",
                        "Building-level power factor tracking",
                    ]
                },
            ]
        },
        {
            "name": "Analytics",
            "icon": "📈",
            "color": "#8B5CF6",
            "bg": "#F5F3FF",
            "border": "#DDD6FE",
            "pages": [
                {
                    "icon": "⚡",
                    "name": "Energy Analytics",
                    "key": "⚡ Energy Analytics",
                    "features": [
                        "Multi-building hourly consumption comparison",
                        "Peak vs off-peak demand analysis",
                        "Temperature & humidity impact on consumption",
                        "Cost and carbon emission trends",
                        "Heatmap: consumption by hour × building",
                        "Load type distribution (peak vs off-peak share)",
                    ]
                },
                {
                    "icon": "🔍",
                    "name": "Telemetry Explorer",
                    "key": "🔍 Telemetry Explorer",
                    "features": [
                        "Full raw dataset with filters (building, hour, date)",
                        "Column-level data quality check",
                        "CSV export of filtered data",
                        "Summary statistics per column",
                    ]
                },
            ]
        },
        {
            "name": "Management",
            "icon": "⚙️",
            "color": "#F59E0B",
            "bg": "#FFFBEB",
            "border": "#FDE68A",
            "pages": [
                {
                    "icon": "🔮",
                    "name": "Scenario Simulator",
                    "key": "🔮 Scenario Simulator",
                    "features": [
                        "Adjust occupancy, ACs, PCs, temperature sliders",
                        "Predicted energy consumption output",
                        "Projected cost and carbon for the scenario",
                        "Compare baseline vs simulated outcome",
                    ]
                },
                {
                    "icon": "🔌",
                    "name": "Load Optimization",
                    "key": "🔌 Load Optimization",
                    "features": [
                        "Identify peak-load windows for shifting",
                        "Equipment scheduling recommendations",
                        "Potential savings from load redistribution",
                        "Priority actions ranked by impact",
                    ]
                },
                {
                    "icon": "💡",
                    "name": "AI Recommendations",
                    "key": "💡 AI Recommendations",
                    "features": [
                        "AI-generated action items with impact estimates",
                        "Priority ranking (high / medium / low)",
                        "Implementation effort vs savings trade-off",
                        "One-click action acknowledgement tracking",
                    ]
                },
                {
                    "icon": "🔔",
                    "name": "Smart Alerts",
                    "key": "🔔 Smart Alerts",
                    "features": [
                        "Real-time threshold breach notifications",
                        "Power factor, voltage, overconsumption alerts",
                        "Severity levels: Critical, Warning, Info",
                        "Alert history and acknowledgement log",
                    ]
                },
            ]
        },
        {
            "name": "System",
            "icon": "🛠️",
            "color": "#64748B",
            "bg": "#F8FAFC",
            "border": "#E2E8F0",
            "pages": [
                {
                    "icon": "📄",
                    "name": "Executive Report",
                    "key": "📄 Executive Report",
                    "features": [
                        "Auto-generated PDF-ready energy summary",
                        "Campus KPI table for board presentations",
                        "Monthly trend overview included",
                    ]
                },
                {
                    "icon": "⚙️",
                    "name": "Settings",
                    "key": "⚙️ Settings",
                    "features": [
                        "Set electricity tariff (₹/kWh)",
                        "Configure carbon emission factor",
                        "Power factor threshold for alerts",
                        "Peak load multiplier and EEI benchmark",
                    ]
                },
                {
                    "icon": "🔮",
                    "name": "Future Integrations",
                    "key": "🔮 Future Integrations",
                    "features": [
                        "IoT sensor integration roadmap",
                        "Real-time SCADA connectivity plan",
                        "ML-based demand forecasting pipeline",
                        "Mobile app and notification system",
                    ]
                },
            ]
        },
    ]

    # ── Role access matrix ────────────────────────────────────────────────────
    ROLE_PAGES = {
        "Director":           ["🏛️ Executive Decision Centre","🏢 Building Drill-Down","⚡ Energy Analytics","💡 AI Recommendations","🔔 Smart Alerts","📄 Executive Report","⚙️ Settings","🗺️ System Guide"],
        "Energy Manager":     ["🏛️ Executive Decision Centre","🏢 Building Drill-Down","⚡ Energy Analytics","🔮 Scenario Simulator","🔌 Load Optimization","💡 AI Recommendations","🔔 Smart Alerts","📄 Executive Report","⚙️ Settings","🗺️ System Guide"],
        "Electrical Engineer":["🏛️ Executive Decision Centre","🏢 Building Drill-Down","⚡ Energy Analytics","🔮 Scenario Simulator","🔌 Load Optimization","🔍 Telemetry Explorer","⚙️ Settings","🗺️ System Guide"],
        "Administrator":      None,  # All pages
    }

    ROLE_COLORS = {
        "Director":            ("#3B82F6", "#EFF6FF"),
        "Energy Manager":      ("#10B981", "#ECFDF5"),
        "Electrical Engineer": ("#F59E0B", "#FFFBEB"),
        "Administrator":       ("#8B5CF6", "#F5F3FF"),
    }

    # ── Hero banner ───────────────────────────────────────────────────────────
    st.markdown("""
<div style="background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 60%,#0F2318 100%);
            border-radius:20px;padding:32px 36px;margin-bottom:28px;
            border:1px solid rgba(255,255,255,0.06);">
    <div style="color:#94A3B8;font-size:0.75rem;font-weight:600;
                letter-spacing:1.2px;text-transform:uppercase;margin-bottom:8px;">
        Navigation Guide
    </div>
    <div style="color:#F1F5F9;font-size:1.6rem;font-weight:800;
                letter-spacing:-0.02em;margin-bottom:10px;line-height:1.2;">
        🗺️ MIET Smart Campus EMS
    </div>
    <div style="color:#64748B;font-size:0.88rem;font-weight:400;
                max-width:560px;line-height:1.6;">
        A complete map of every page in this system — what data you can retrieve,
        what actions you can take, and which roles have access.
    </div>
    <div style="display:flex;gap:8px;margin-top:16px;flex-wrap:wrap;">
        <span style="background:#10B98120;color:#10B981;padding:5px 14px;
                     border-radius:20px;font-size:0.75rem;font-weight:700;
                     border:1px solid #10B98140;">● 11 Pages</span>
        <span style="background:#3B82F620;color:#60A5FA;padding:5px 14px;
                     border-radius:20px;font-size:0.75rem;font-weight:700;
                     border:1px solid #3B82F640;">4 Categories</span>
        <span style="background:#F59E0B20;color:#F59E0B;padding:5px 14px;
                     border-radius:20px;font-size:0.75rem;font-weight:700;
                     border:1px solid #F59E0B40;">4 User Roles</span>
    </div>
</div>
""", unsafe_allow_html=True)

    # ── Flow map — category columns ───────────────────────────────────────────
    for cat in categories:
        st.markdown(f"""
<div style="background:{cat['bg']};border:1px solid {cat['border']};
            border-radius:16px;padding:20px 22px;margin-bottom:16px;">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">
        <div style="background:{cat['color']}20;width:36px;height:36px;border-radius:10px;
                    display:flex;align-items:center;justify-content:center;font-size:1.1rem;">
            {cat['icon']}
        </div>
        <div>
            <div style="font-size:0.65rem;font-weight:700;color:{cat['color']};
                        text-transform:uppercase;letter-spacing:1px;">Category</div>
            <div style="font-size:1rem;font-weight:800;color:#0F172A;">{cat['name']}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

        # Page cards inside each category
        page_cols = st.columns(len(cat["pages"]))
        for i, page in enumerate(cat["pages"]):
            features_html = "".join(
                f'<li style="font-size:0.77rem;color:#475569;margin-bottom:4px;line-height:1.4;">{f}</li>'
                for f in page["features"]
            )
            with page_cols[i]:
                st.markdown(f"""
<div style="background:white;border-radius:14px;padding:18px;
            border:1px solid #E2E8F0;
            box-shadow:0 2px 8px rgba(0,0,0,0.04);
            height:100%;">
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
        <span style="font-size:1.3rem;">{page['icon']}</span>
        <span style="font-size:0.9rem;font-weight:700;color:#0F172A;">{page['name']}</span>
    </div>
    <div style="font-size:0.68rem;font-weight:600;color:{cat['color']};
                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;">
        What you can retrieve
    </div>
    <ul style="margin:0;padding-left:14px;">
        {features_html}
    </ul>
</div>
""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Role Access Matrix ─────────────────────────────────────────────────────
    st.markdown("""
<div style="margin-top:8px;margin-bottom:16px;">
    <div style="font-size:0.7rem;font-weight:700;color:#64748B;
                text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">
        Role Access Matrix
    </div>
</div>
""", unsafe_allow_html=True)

    all_pages = [p["key"] for cat in categories for p in cat["pages"]]
    roles = ["Director", "Energy Manager", "Electrical Engineer", "Administrator"]

    header_cols = st.columns([2.5] + [1] * len(roles))
    with header_cols[0]:
        st.markdown("<div style='font-size:0.78rem;font-weight:700;color:#0F172A;padding:8px 0;'>Page</div>", unsafe_allow_html=True)
    for j, role in enumerate(roles):
        color, bg = ROLE_COLORS[role]
        with header_cols[j + 1]:
            st.markdown(f"""
<div style="text-align:center;background:{bg};color:{color};
            padding:6px 4px;border-radius:8px;font-size:0.7rem;
            font-weight:700;border:1px solid {color}30;">
    {role.split()[0]}
</div>
""", unsafe_allow_html=True)

    for page_key in all_pages:
        row_cols = st.columns([2.5] + [1] * len(roles))
        page_label = page_key.split(" ", 1)[1] if " " in page_key else page_key
        with row_cols[0]:
            icon = page_key.split(" ")[0]
            st.markdown(f"""
<div style="font-size:0.8rem;color:#374151;padding:8px 0;
            border-bottom:1px solid #F1F5F9;font-weight:500;">
    {icon} {page_label}
</div>
""", unsafe_allow_html=True)
        for j, role in enumerate(roles):
            color, _ = ROLE_COLORS[role]
            allowed = ROLE_PAGES[role] is None or page_key in ROLE_PAGES[role]
            icon_html = f'<span style="color:{color};font-size:1rem;">✓</span>' if allowed else '<span style="color:#CBD5E1;font-size:0.9rem;">—</span>'
            with row_cols[j + 1]:
                st.markdown(f"""
<div style="text-align:center;padding:8px 0;border-bottom:1px solid #F1F5F9;">
    {icon_html}
</div>
""", unsafe_allow_html=True)
