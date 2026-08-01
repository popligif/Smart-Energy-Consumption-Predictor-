"""
Shared CSS Design System — Midnight Energy Theme
Injected ONCE per session, not on every rerun.
"""
import streamlit as st


def inject_styles():
    """
    Inject global CSS design system. Uses session state flag so CSS
    is only sent over WebSocket once per browser session.
    """
    if st.session_state.get("_styles_injected"):
        return
    st.session_state["_styles_injected"] = True

    st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Main content area ── */
.main .block-container {
    padding-top: 0 !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 100% !important;
    background: #F1F5F9;
}
.main { background-color: #F1F5F9 !important; }

/* ── Page transition ── */
.main .block-container {
    animation: pageSlideUp 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}
@keyframes pageSlideUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Sidebar: Midnight Energy theme ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E293B 60%, #0F2318 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.04) !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.35) !important;
    width: 260px !important;
}
section[data-testid="stSidebar"] > div { background: transparent !important; }

/* Nav pills */
section[data-testid="stSidebar"] .stRadio > div { gap: 2px; }
section[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    padding: 9px 14px;
    border-radius: 10px;
    transition: all 0.18s ease;
    cursor: pointer;
    border: 1px solid transparent;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(16,185,129,0.12);
    border-color: rgba(16,185,129,0.2);
    transform: translateX(3px);
}
section[data-testid="stSidebar"] .stRadio div[data-testid="stMarkdownContainer"] p {
    font-size: 0.88rem;
    font-weight: 500;
    color: #94A3B8 !important;
}
section[data-testid="stSidebar"] * { color: #94A3B8 !important; }
section[data-testid="stSidebar"] hr {
    border-top: 1px solid rgba(255,255,255,0.07) !important;
    margin: 10px 0 !important;
}

/* Selectbox in sidebar */
section[data-testid="stSidebar"] .stSelectbox label {
    color: #64748B !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 22px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    border: 1px solid #E2E8F0;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
    height: 100%;
}
.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(15,23,42,0.10);
}
.kpi-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    margin-bottom: 14px;
}
.kpi-label { font-size: 0.78rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 6px; }
.kpi-value { font-size: 2rem; font-weight: 800; color: #0F172A; line-height: 1.1; letter-spacing: -0.03em; }
.kpi-unit  { font-size: 0.9rem; font-weight: 500; color: #94A3B8; margin-left: 4px; }
.kpi-delta { font-size: 0.78rem; font-weight: 600; margin-top: 8px; display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 20px; }
.kpi-delta.up   { color: #10B981; background: #ECFDF5; }
.kpi-delta.down { color: #EF4444; background: #FEF2F2; }
.kpi-delta.warn { color: #F59E0B; background: #FFFBEB; }

/* ── Section Headers ── */
.section-header {
    display: flex; align-items: center; gap: 10px;
    margin: 28px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 2px solid #E2E8F0;
}
.section-header h3 {
    font-size: 1rem; font-weight: 700;
    color: #0F172A; margin: 0;
    letter-spacing: -0.01em;
}
.section-badge {
    font-size: 0.7rem; font-weight: 600;
    padding: 3px 10px; border-radius: 20px;
    background: #EFF6FF; color: #3B82F6;
}

/* ── Building Cards ── */
.building-card {
    background: white;
    border-radius: 14px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    border: 1px solid #F1F5F9;
    border-left: 4px solid #10B981;
    margin-bottom: 8px;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.building-card:hover { transform: scale(1.01); box-shadow: 0 4px 16px rgba(0,0,0,0.08); }

/* ── Equipment Cards ── */
.equip-card {
    background: white;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    border: 1px solid #E2E8F0;
    text-align: center;
}

/* ── Page Title Header ── */
.page-title-bar {
    background: white;
    border-radius: 16px;
    padding: 18px 24px;
    margin-bottom: 24px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    display: flex;
    align-items: center;
    gap: 14px;
}
.page-title-bar .icon-box {
    width: 46px; height: 46px;
    border-radius: 12px;
    display: flex; align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
}
.page-title-bar h2 { margin: 0; font-size: 1.1rem; font-weight: 700; color: #0F172A; }
.page-title-bar p  { margin: 0; font-size: 0.82rem; color: #64748B; font-weight: 400; }

/* ── Flow Map ── */
.flow-category { border-radius: 14px; padding: 18px; margin-bottom: 12px; }
.flow-page-card {
    background: white;
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 8px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.flow-page-card h5 { margin: 0 0 6px 0; font-size: 0.88rem; font-weight: 700; color: #0F172A; }
.flow-page-card ul { margin: 0; padding-left: 16px; }
.flow-page-card li { font-size: 0.78rem; color: #64748B; margin-bottom: 2px; }

/* ── Role badges ── */
.role-badge {
    display: inline-block;
    padding: 3px 12px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 600;
    margin: 2px;
}

/* ── Metric deltas ── */
.delta-up   { color: #10B981; font-weight: 700; font-size: 0.82rem; background: #ECFDF5; padding: 2px 8px; border-radius: 10px; }
.delta-down { color: #EF4444; font-weight: 700; font-size: 0.82rem; background: #FEF2F2; padding: 2px 8px; border-radius: 10px; }
.metric-val { font-size: 2.2rem; font-weight: 800; color: #0F172A; line-height: 1.1; letter-spacing: -0.02em; }
.metric-sub { font-size: 0.82rem; color: #64748B; margin-top: 4px; font-weight: 500; }

/* ── Misc ── */
button[title="View fullscreen"] { display: none; }
.stAlert { border-radius: 12px !important; }
.stDataFrame { border-radius: 12px !important; border: 1px solid #E2E8F0 !important; }
div[data-testid="stExpander"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    background: white !important;
}
</style>
""", unsafe_allow_html=True)
