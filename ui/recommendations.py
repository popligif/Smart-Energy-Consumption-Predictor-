"""
AI Recommendations page — Redesigned to match enterprise UI.
Fixes HTML-rendering-as-raw-text bug by using html.escape() on all dynamic data.
"""
import html
import streamlit as st
from services.recommendation_service import RecommendationService


def _e(text: str) -> str:
    """HTML-escape a string so special chars don't break the rendered card."""
    return html.escape(str(text), quote=False)


def render_recommendations() -> None:
    recommender = RecommendationService()
    recs        = recommender.generate_recommendations()

    tot_savings_inr = sum(r["Annual Savings (INR)"]          for r in recs)
    tot_offset_co2  = sum(r["Annual Carbon Offset (kg CO2)"] for r in recs)

    # ── Section header ─────────────────────────────────────────────────────────


    # ── Savings Banner ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#ECFDF5,#D1FAE5);
                border:1px solid #6EE7B7;padding:20px 24px;border-radius:14px;
                margin-bottom:20px;">
      <div style="font-size:0.75rem;font-weight:700;color:#059669;
                   text-transform:uppercase;margin-bottom:6px;">
        Total Campus Savings Potential — {len(recs)} Actions Identified
      </div>
      <div style="display:flex;gap:40px;align-items:center;flex-wrap:wrap;">
        <div>
          <div style="font-size:0.78rem;color:#065F46;font-weight:600;">
            Annual Cost Reduction
          </div>
          <div style="font-size:2rem;font-weight:800;color:#064E3B;">
            ₹{tot_savings_inr:,.0f} <span style="font-size:1rem;font-weight:500;">/ year</span>
          </div>
        </div>
        <div style="width:1px;height:50px;background:#A7F3D0;"></div>
        <div>
          <div style="font-size:0.78rem;color:#065F46;font-weight:600;">
            Annual Carbon Mitigation
          </div>
          <div style="font-size:2rem;font-weight:800;color:#064E3B;">
            {tot_offset_co2:,.0f} <span style="font-size:1rem;font-weight:500;">kg CO₂ / yr</span>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Filters ────────────────────────────────────────────────────────────────
    col_f1, col_f2 = st.columns(2, gap="medium")
    with col_f1:
        cats = ["All"] + sorted({r["Category"] for r in recs})
        cat_filter = st.selectbox("Filter by Category", cats, key="rec_cat")
    with col_f2:
        confs = ["All", "High", "Medium", "Low"]
        conf_filter = st.selectbox("Filter by Confidence", confs, key="rec_conf")

    filtered = recs
    if cat_filter  != "All": filtered = [r for r in filtered if r["Category"] == cat_filter]
    if conf_filter != "All": filtered = [r for r in filtered if r["Confidence"] == conf_filter]

    st.markdown(f"""
    <div style="font-size:0.82rem;color:#64748B;margin:8px 0 16px 0;">
      Showing <b>{len(filtered)}</b> recommendation(s)
    </div>
    """, unsafe_allow_html=True)

    # ── Recommendation Cards ───────────────────────────────────────────────────
    for r in filtered:
        conf       = _e(r["Confidence"])
        category   = _e(r["Category"])
        title      = _e(r["Title"])
        details    = _e(r["Details"])
        trigger    = _e(r["Trigger"])
        reasoning  = _e(r["Reasoning"])
        savings    = r["Annual Savings (INR)"]
        carbon     = r["Annual Carbon Offset (kg CO2)"]

        conf_color = (
            "#10B981" if conf == "High"
            else "#F59E0B" if conf == "Medium"
            else "#EF4444"
        )
        bg = "#F0FDF4" if conf == "High" else "#FFFBEB" if conf == "Medium" else "#FEF2F2"

        # Build the card as a plain Python string — no nested f-strings
        card_html = (
            '<div style="background:white;border:1px solid #F1F5F9;'
            'border-left:5px solid ' + conf_color + ';'
            'border-radius:12px;padding:20px;margin-bottom:16px;'
            'box-shadow:0 1px 4px rgba(0,0,0,0.05);">'

            # Header row
            '<div style="display:flex;justify-content:space-between;'
            'align-items:flex-start;margin-bottom:10px;">'
            '<div>'
            '<span style="font-size:0.72rem;color:#94A3B8;text-transform:uppercase;'
            'font-weight:700;letter-spacing:0.5px;">' + category + '</span>'
            '<div style="font-size:1.05rem;font-weight:700;color:#0F172A;margin-top:3px;">'
            + title + '</div>'
            '</div>'
            '<span style="background:' + bg + ';color:' + conf_color + ';'
            'font-size:0.72rem;font-weight:700;padding:4px 12px;border-radius:20px;'
            'border:1px solid ' + conf_color + ';white-space:nowrap;">'
            + conf + ' Confidence'
            '</span>'
            '</div>'

            # Proposed action
            '<div style="font-size:0.85rem;color:#374151;margin-bottom:10px;line-height:1.6;">'
            '<b>Proposed Action:</b> ' + details + '</div>'

            # Triggering telemetry
            '<div style="background:#F8FAFC;padding:10px 14px;border-radius:8px;'
            'font-size:0.82rem;color:#4B5563;margin-bottom:10px;'
            'border-left:3px solid #CBD5E0;">'
            '<b>Triggering Telemetry:</b> <i>' + trigger + '</i></div>'

            # Financial metrics
            '<div style="display:flex;gap:24px;font-size:0.82rem;'
            'font-weight:700;margin-bottom:10px;flex-wrap:wrap;">'
            '<span style="color:#059669;">&#x1F4B0; Est. Annual Savings: '
            '&#8377;' + f'{savings:,.0f}' + '</span>'
            '<span style="color:#0891B2;">&#x1F331; Carbon Offset: '
            + f'{carbon:,.0f}' + ' kg CO&#8322;</span>'
            '</div>'

            # AI reasoning
            '<div style="font-size:0.8rem;color:#6B7280;line-height:1.5;'
            'border-top:1px solid #F1F5F9;padding-top:10px;">'
            '<b>Explainable AI Reasoning:</b> ' + reasoning + '</div>'
            '</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)
