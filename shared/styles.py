import streamlit as st

def inject_styles():
    # Always inject styles on every run so that navigation page transitions don't lose the CSS.
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Base Variables & App Level */
    :root {
        --bg-color: #F1F5F9;
        --text-main: #0F172A;
        --text-muted: #64748B;
        --emerald: #10B981;
        --amber: #F59E0B;
        --violet: #8B5CF6;
        --sky: #06B6D4;
        --rose: #EF4444;
    }
    
    .stApp {
        background-color: var(--bg-color);
        background-image: radial-gradient(#E2E8F0 1.5px, transparent 1.5px);
        background-size: 24px 24px;
        font-family: 'Inter', sans-serif;
        color: var(--text-main);
    }

    /* Streamlit Default Header Adjustments */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 99 !important;
    }

    /* Sidebar Styling - Premium Dark Emerald Green Theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #064E3B 0%, #022C22 100%) !important;
        min-width: 260px;
        max-width: 260px;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }
    
    /* Scrollbar */
    [data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 4px;
    }
    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background: var(--emerald);
        border-radius: 4px;
    }

    /* Sidebar Radio/Nav Pills */
    .stRadio > div {
        gap: 6px;
    }
    .stRadio > div > label {
        background: transparent;
        border-radius: 8px;
        padding: 8px 12px;
        transition: all 0.2s ease;
        cursor: pointer;
        border: 1px solid transparent;
        margin-bottom: 2px;
    }
    .stRadio > div > label:hover {
        background: rgba(16, 185, 129, 0.15) !important;
        transform: translateX(3px);
        border-color: rgba(16, 185, 129, 0.3) !important;
    }
    .stRadio > div > label[data-checked="true"] {
        background: rgba(16, 185, 129, 0.25) !important;
        border-color: var(--emerald) !important;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1);
    }
    .stRadio > div > label div[data-testid="stMarkdownContainer"] p {
        font-size: 14px;
        margin: 0;
        color: #F8FAFC !important;
    }

    /* Page Transition */
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .block-container {
        animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
    }

    /* Generic Cards */
    .kpi-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease;
        border: 1px solid #E2E8F0;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
    }

    /* KPI Icons */
    .kpi-icon {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
        flex-shrink: 0;
    }
    .kpi-icon.emerald { background: linear-gradient(135deg, #10B981, #059669); color: white; }
    .kpi-icon.sky { background: linear-gradient(135deg, #38BDF8, #0284C7); color: white; }
    .kpi-icon.violet { background: linear-gradient(135deg, #A78BFA, #7C3AED); color: white; }
    .kpi-icon.amber { background: linear-gradient(135deg, #FBBF24, #D97706); color: white; }
    .kpi-icon.rose { background: linear-gradient(135deg, #FB7185, #E11D48); color: white; }

    /* Typography & Metrics */
    .metric-val {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
        margin: 4px 0;
        color: var(--text-main);
        letter-spacing: -0.02em;
    }
    .metric-sub {
        font-size: 0.82rem;
        color: var(--text-muted);
        font-weight: 500;
        margin: 0;
    }

    /* Badges */
    .delta-badge {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 8px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .delta-up { background: rgba(16,185,129,0.1); color: var(--emerald); }
    .delta-down { background: rgba(239,68,68,0.1); color: var(--rose); }
    .delta-warn { background: rgba(245,158,11,0.1); color: var(--amber); }

    /* Headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid var(--emerald);
        margin-bottom: 16px;
    }
    .section-header h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-main);
    }

    /* Building Cards */
    .building-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        border-left: 4px solid var(--emerald);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        margin-bottom: 12px;
    }
    .building-card:hover {
        transform: scale(1.02);
    }

    /* Page Title Bar */
    .page-title-bar {
        background: white;
        border-radius: 16px;
        padding: 20px 24px;
        display: flex;
        align-items: center;
        gap: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin-bottom: 24px;
        border: 1px solid #E2E8F0;
    }

    /* Flow Map Cards */
    .flow-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Forecast Ring Animation */
    @keyframes pulseRing {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
    .forecast-ring {
        animation: pulseRing 2s infinite;
        border-radius: 50%;
    }

    /* Streamlit Overrides */
    button[title="View fullscreen"] {
        display: none;
    }
    .stExpander {
        border: 1px solid #E2E8F0;
        border-radius: 12px !important;
        background: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 8px 8px 0 0;
        padding: 8px 16px;
        border: 1px solid #E2E8F0;
        border-bottom: none;
    }
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }
    </style>
    """, unsafe_allow_html=True)
