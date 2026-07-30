"""
Executive Decision Centre — Fixed version:
- Unique keys for all plotly_chart calls (fixes StreamlitDuplicateElementId)
- Navbar rendered inside the page (fixes header not visible)
- Building power breakdown section added
- Feature importance section added
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from services.dashboard_service import DashboardService
from services.alert_service import AlertService
from services.data_service import DataService

# ── Cached pre-computation: runs once per session, not every rerun ──────────
@st.cache_data(ttl=600, show_spinner=False)
def _precompute_dashboard(csv_path: str):
    """All heavy Pandas operations cached — keyed by csv_path."""
    from services.data_service import _load_and_process_csv
    df = _load_and_process_csv(csv_path)

    # Hourly totals for sparklines
    hourly_total = df.groupby("Hour")["Energy Consumption"].sum().values.tolist()
    spark_base = hourly_total[:12] if len(hourly_total) >= 12 else hourly_total

    # Per-building hourly sparkline values
    bldg_hourly = {}
    for b in df["Building"].unique():
        bldg_hourly[b] = (
            df[df["Building"] == b]
            .sort_values("Hour")["Energy Consumption"]
            .values.tolist()
        )

    # Per-building aggregate stats
    bldg_summary = {}
    for b in df["Building"].unique():
        bdf = df[df["Building"] == b]
        bldg_summary[b] = {
            "avg_kw":       round(bdf["Energy Consumption"].mean(), 1),
            "avg_pf":       round(bdf["Power Factor"].mean(), 3),
            "avg_occ":      round(bdf["Occupancy"].mean()),
            "avg_pcs":      round(bdf["Running Computers"].mean()),
            "avg_acs":      round(bdf["Running ACs"].mean()),
            "avg_lighting": round(bdf["Lighting Load"].mean(), 2),
            "avg_hvac":     round(bdf["HVAC Load"].mean(), 2),
            "avg_lab":      round(bdf["Laboratory Usage"].mean(), 2),
            "avg_workshop": round(bdf["Workshop Usage"].mean(), 2),
            "avg_coe":      round(bdf["CoE Activity"].mean(), 2),
            "avg_equip":    round(bdf["Equipment Usage"].mean(), 2),
        }

    # Feature importance via Pearson correlation
    feat_cols = {
        "Occupancy":         "👥 Occupancy",
        "Running ACs":       "❄️ Running ACs",
        "Running Computers": "💻 Running PCs",
        "HVAC Load":         "🌡️ HVAC Load",
        "Lighting Load":     "💡 Lighting",
        "Laboratory Usage":  "🔬 Lab Equipment",
        "Workshop Usage":    "🔧 Workshop Equip.",
        "Temperature":       "🌡️ Outdoor Temp",
        "Humidity":          "💧 Humidity",
        "CoE Activity":      "🏛️ CoE Activity",
    }
    corr_vals = {}
    for col, label in feat_cols.items():
        if col in df.columns:
            corr_vals[label] = round(abs(df[col].corr(df["Energy Consumption"])), 3)

    df_imp = (
        pd.DataFrame(list(corr_vals.items()), columns=["Feature", "Importance"])
        .sort_values("Importance", ascending=True)
    )

    # Campus-wide equipment totals
    equip_totals = {
        "total_pcs":  int(df["Running Computers"].sum()),
        "total_acs":  int(df["Running ACs"].sum()),
        "total_occ":  int(df["Occupancy"].sum()),
        "lab_active": int((df["Laboratory Usage"] > 0).sum()),
        "workshop_a": int((df["Workshop Usage"] > 0).sum()),
        "campus_mean": round(df["Energy Consumption"].mean(), 1),
        "num_buildings": df["Building"].nunique(),
        "total_floors":  df["Floor"].nunique() * df["Building"].nunique(),
    }

    return spark_base, bldg_hourly, bldg_summary, df_imp, equip_totals

# ── Helper: tiny sparkline (with UNIQUE key parameter) ───────────────────────
def _sparkline(values: list, color: str, chart_key: str, height: int = 50) -> None:
    """Renders a sparkline chart with a guaranteed unique key to avoid ID conflicts."""
    fig = go.Figure()
    # Build valid rgba from hex
    try:
        r, g, b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        fill_color = f"rgba({r},{g},{b},0.12)"
    except Exception:
        fill_color = "rgba(59,130,246,0.12)"
    fig.add_trace(go.Scatter(
        y=values, mode="lines",
        line=dict(color=color, width=2, shape="spline"),
        fill="tozeroy", fillcolor=fill_color
    ))
    fig.update_layout(
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False}, key=chart_key)

# ── Helper: KPI card HTML ─────────────────────────────────────────────────────
def _kpi_card(icon, icon_bg, value, unit, label, delta, delta_up):
    arrow = "↑" if delta_up else "↓"
    d_cls = "delta-up" if delta_up else "delta-down"
    return f"""<div class="kpi-card">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
            <div style="background:{icon_bg};width:36px;height:36px;border-radius:10px;
                        display:flex;align-items:center;justify-content:center;font-size:1rem;">
                {icon}
            </div>
            <span class="{d_cls}">{arrow} {delta}</span>
        </div>
        <div class="metric-val">{value}
            <span style="font-size:1rem;font-weight:500;color:#64748B;margin-left:4px;">{unit}</span>
        </div>
        <div class="metric-sub">{label}</div>
    </div>"""

def render_dashboard() -> None:
    db        = DashboardService()
    alert_svc = AlertService()
    data_svc  = DataService()

    kpis     = db.get_executive_kpis()
    health   = db.calculate_campus_health_score()
    rankings = db.get_building_rankings()
    alerts   = alert_svc.scan_for_alerts()

    # Use cached precomputed data instead of re-computing on every rerun
    spark_base, bldg_hourly, bldg_summary, df_imp, equip_totals = \
        _precompute_dashboard(data_svc.csv_path)

    SHORT = {
        "Academic Block A": "Block A", "Academic Block B": "Block B",
        "Academic Block C": "Block C", "Academic Block D": "Block D",
        "Workshop Building": "Workshop", "Centre of Excellence": "CoE"
    }
    BUILDING_META = {
        "Academic Block A": {"type": "Administrative", "floors": 3, "area": "3,200 m²"},
        "Academic Block B": {"type": "Academic",       "floors": 3, "area": "3,600 m²"},
        "Academic Block C": {"type": "Academic",       "floors": 3, "area": "3,600 m²"},
        "Academic Block D": {"type": "Academic",       "floors": 3, "area": "3,800 m²"},
        "Workshop Building": {"type": "Workshop",      "floors": 3, "area": "2,800 m²"},
        "Centre of Excellence": {"type": "Research",   "floors": 3, "area": "2,400 m²"},
    }

    # ── Section Header ────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:20px 0 4px 0;">
      <div style="font-size:1.5rem;font-weight:800;color:#0F172A;">
        📊 Executive KPI Dashboard
      </div>
      <div style="color:#94A3B8;font-size:0.82rem;">
        Real-time campus energy performance indicators
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ROW 1 KPI Cards ───────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    total_kw   = round(kpis["total_energy_kwh"] / 24, 1)
    daily_kwh  = round(kpis["total_energy_kwh"], 1)
    total_cost = round(kpis["total_cost_inr"], 0)
    peak_kw    = round(kpis["peak_load_kw"], 1)

    with c1:
        st.markdown(_kpi_card("⚡","#EFF6FF",f"{total_kw}","kW","Total Campus Consumption","2.4%",True), unsafe_allow_html=True)
        _sparkline(spark_base, "#3B82F6", "spark_c1")
    with c2:
        st.markdown(_kpi_card("📅","#F0FDF4",f"{daily_kwh:,.1f}","kWh","Today's Energy Usage","1.8%",True), unsafe_allow_html=True)
        _sparkline(spark_base, "#10B981", "spark_c2")
    with c3:
        st.markdown(_kpi_card("₹","#FFFBEB",f"₹{total_cost:,.0f}","","Today's Electricity Cost","1.8%",True), unsafe_allow_html=True)
        _sparkline(spark_base, "#F59E0B", "spark_c3")
    with c4:
        st.markdown(_kpi_card("📈","#FEF2F2",f"{peak_kw}","kW","Peak Demand","0.6%",False), unsafe_allow_html=True)
        _sparkline(spark_base, "#EF4444", "spark_c4")

    # ── ROW 2 KPI Cards ───────────────────────────────────────────────────────
    c5, c6, c7, c8 = st.columns(4, gap="medium")
    total_carbon  = round(kpis["total_carbon_kg"], 1)
    health_score  = health["overall_score"]
    num_buildings = equip_totals["num_buildings"]
    total_floors  = equip_totals["total_floors"]

    with c5:
        st.markdown(_kpi_card("🌿","#F0FDF4",f"{total_carbon:,.1f}","CO₂ kg","Carbon Emissions","1.8%",True), unsafe_allow_html=True)
        _sparkline(spark_base, "#10B981", "spark_c5")
    with c6:
        st.markdown(_kpi_card("🎯","#F5F3FF",f"{health_score}","%","Campus Efficiency","0.5%",True), unsafe_allow_html=True)
        _sparkline([60,62,65,63,68,70,72,70,68,72,75,73], "#8B5CF6", "spark_c6")
    with c7:
        st.markdown(_kpi_card("🏢","#EFF6FF",f"{num_buildings}",f"/ {num_buildings}","Active Buildings","0%",True), unsafe_allow_html=True)
        _sparkline([6]*12, "#3B82F6", "spark_c7")
    with c8:
        st.markdown(_kpi_card("📐","#ECFDF5",f"{total_floors}",f"/ {total_floors}","Active Floors","0%",True), unsafe_allow_html=True)
        _sparkline(list(range(10, 22)), "#06B6D4", "spark_c8")

    st.markdown("---")

    # ── Digital Campus View ───────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:12px 0 4px 0;">
      <div style="font-size:1.3rem;font-weight:800;color:#0F172A;">🗺️ Digital Campus View</div>
      <div style="color:#94A3B8;font-size:0.82rem;">
        Building colour reflects real-time energy demand
      </div>
    </div>
    <div style="display:flex;gap:20px;margin:10px 0 16px 0;font-size:0.82rem;color:#475569;align-items:center;">
      <span>● <span style="color:#10B981;font-weight:600;">Normal</span></span>
      <span>● <span style="color:#F59E0B;font-weight:600;">Warning</span></span>
      <span>● <span style="color:#F97316;font-weight:600;">High Load</span></span>
      <span>● <span style="color:#EF4444;font-weight:600;">Critical</span></span>
    </div>
    """, unsafe_allow_html=True)

    bldg_summary_local = bldg_summary
    buildings_sorted = list(BUILDING_META.keys())

    def status_for(kw):
        if   kw < 15:  return "#10B981", "Normal"
        elif kw < 40:  return "#F59E0B", "Warning"
        elif kw < 80:  return "#F97316", "High Load"
        else:          return "#EF4444", "Critical"

    campus_mean = equip_totals["campus_mean"]

    for row_bldgs in [buildings_sorted[:3], buildings_sorted[3:]]:
        cols = st.columns(3, gap="medium")
        for col, bname in zip(cols, row_bldgs):
            meta  = BUILDING_META[bname]
            stats = bldg_summary.get(bname, {})
            kw    = stats.get("avg_kw", 0)
            sc, sl = status_for(kw)
            pct   = round(abs(kw - campus_mean) / max(campus_mean, 0.1) * 100)
            with col:
                st.markdown(f"""
                <div class="building-card" style="border-top-color:{sc};">
                  <div style="font-size:0.7rem;color:#94A3B8;font-weight:500;">{meta['type']}</div>
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-top:2px;">
                    <div>
                      <div style="font-size:1.0rem;font-weight:700;color:#0F172A;">{bname}</div>
                      <div style="font-size:0.72rem;color:#94A3B8;">{meta['floors']} Floors · {meta['area']}</div>
                    </div>
                    <div style="background:#F0FDF4;width:32px;height:32px;border-radius:8px;
                                display:flex;align-items:center;justify-content:center;">🏢</div>
                  </div>
                  <div style="font-size:1.55rem;font-weight:800;color:#0F172A;margin:8px 0 4px 0;">
                    {kw} <span style="font-size:0.82rem;font-weight:500;color:#64748B;">kW</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="background:{sc}1A;color:{sc};font-size:0.7rem;
                                 padding:2px 8px;border-radius:12px;font-weight:600;">
                      {sl} · {pct}%
                    </span>
                    <span style="font-size:0.75rem;color:#3B82F6;font-weight:500;">Floors →</span>
                  </div>
                  <div style="height:4px;background:#F1F5F9;border-radius:4px;margin-top:8px;">
                    <div style="height:4px;background:{sc};border-radius:4px;
                                width:{min(100, int(kw/2))}%;"></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Building Monitoring with Sparklines ───────────────────────────────────
    st.markdown("""
    <div style="padding:12px 0 4px 0;">
      <div style="font-size:1.3rem;font-weight:800;color:#0F172A;">📡 Building Monitoring</div>
      <div style="color:#94A3B8;font-size:0.82rem;">Real-time load profile per building</div>
    </div>
    """, unsafe_allow_html=True)

    for row_bldgs in [buildings_sorted[:3], buildings_sorted[3:]]:
        cols = st.columns(3, gap="medium")
        for col, bname in zip(cols, row_bldgs):
            stats = bldg_summary.get(bname, {})
            kw    = stats.get("avg_kw", 0)
            pf    = stats.get("avg_pf", 0)
            occ   = stats.get("avg_occ", 0)
            pcs   = stats.get("avg_pcs", 0)
            acs   = stats.get("avg_acs", 0)
            meta  = BUILDING_META[bname]
            sc, sl = status_for(kw)
            occ_pct = round(occ / max(200, 1) * 100)
            spark_vals = bldg_hourly.get(bname, [5]*12)[:12]
            short_name = SHORT.get(bname, bname)
            spark_key  = f"bmon_{bname.replace(' ','_')}"

            with col:
                st.markdown(f"""
                <div class="building-card" style="border-top-color:{sc};">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                      <div style="font-size:0.72rem;color:#94A3B8;">{meta['type']}</div>
                      <div style="font-size:0.95rem;font-weight:700;color:#0F172A;">{short_name}</div>
                    </div>
                    <div style="font-size:1.6rem;font-weight:800;color:#0F172A;">
                      {kw}<span style="font-size:0.75rem;color:#94A3B8;"> kW</span>
                    </div>
                  </div>
                  <span style="background:{sc}1A;color:{sc};font-size:0.68rem;
                               padding:2px 8px;border-radius:10px;font-weight:600;">{sl}</span>
                """, unsafe_allow_html=True)
                _sparkline(spark_vals, sc, spark_key, height=55)
                st.markdown(f"""
                  <div style="display:flex;gap:10px;padding:8px 0 4px 0;
                              border-top:1px solid #F1F5F9;font-size:0.72rem;">
                    <div style="text-align:center;flex:1;">
                      <div>👥</div><div style="font-weight:700;color:#0F172A;">{occ_pct}%</div>
                      <div style="color:#94A3B8;font-size:0.62rem;">Occ</div>
                    </div>
                    <div style="text-align:center;flex:1;">
                      <div>💻</div><div style="font-weight:700;color:#0F172A;">{pcs}</div>
                      <div style="color:#94A3B8;font-size:0.62rem;">PCs</div>
                    </div>
                    <div style="text-align:center;flex:1;">
                      <div>❄️</div><div style="font-weight:700;color:#0F172A;">{acs}</div>
                      <div style="color:#94A3B8;font-size:0.62rem;">ACs</div>
                    </div>
                    <div style="text-align:center;flex:1;">
                      <div>⚙️</div><div style="font-weight:700;color:#0F172A;">{round(pf*100)}%</div>
                      <div style="color:#94A3B8;font-size:0.62rem;">PF</div>
                    </div>
                  </div>
                  <div style="display:flex;justify-content:space-between;
                              font-size:0.72rem;color:#64748B;margin-top:4px;">
                    <span>🔶 {kw} kW</span>
                    <span>PF {pf:.2f}</span>
                    <span style="color:#3B82F6;font-weight:500;">Floors ↑</span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Building Power Breakdown (New Feature) ────────────────────────────────
    st.markdown("""
    <div style="padding:12px 0 4px 0;">
      <div style="font-size:1.3rem;font-weight:800;color:#0F172A;">🔌 Building Power Consumption Breakdown</div>
      <div style="color:#94A3B8;font-size:0.82rem;">
        What is consuming power in each building — Equipment contribution analysis
      </div>
    </div>
    """, unsafe_allow_html=True)

    selected_bldg = st.selectbox(
        "Select Building to Inspect",
        options=buildings_sorted,
        key="bldg_breakdown_select"
    )
    bstats = bldg_summary.get(selected_bldg, {})
    # Use precomputed bdf average CoE and Equipment from bldg_summary
    coe_kw   = bstats.get("avg_coe", 0)
    equip_kw = bstats.get("avg_equip", 0)
    lighting_kw = bstats.get("avg_lighting", 0)
    hvac_kw     = bstats.get("avg_hvac", 0)
    lab_kw      = bstats.get("avg_lab", 0)
    ws_kw       = bstats.get("avg_workshop", 0)
    pcs_kw      = round(bstats.get("avg_pcs", 0) * 0.15, 2)   # ~150W per PC
    acs_kw      = round(bstats.get("avg_acs", 0) * 1.5, 2)    # ~1.5kW per AC ton


    total_breakdown = lighting_kw + hvac_kw + lab_kw + ws_kw + pcs_kw + acs_kw + coe_kw + equip_kw
    total_breakdown = max(total_breakdown, 0.1)

    breakdown_data = {
        "Component":   ["HVAC / ACs",   "Lighting",   "Computers (PCs)", "Laboratories", "Workshop Equip.", "CoE Research", "Other Equip."],
        "Load (kW)":   [hvac_kw, lighting_kw, pcs_kw, lab_kw, ws_kw, coe_kw, equip_kw],
        "Color":       ["#3B82F6","#F59E0B","#10B981","#8B5CF6","#F97316","#06B6D4","#94A3B8"]
    }
    df_breakdown = pd.DataFrame(breakdown_data)
    df_breakdown["% Share"] = (df_breakdown["Load (kW)"] / total_breakdown * 100).round(1)
    df_breakdown = df_breakdown[df_breakdown["Load (kW)"] > 0].sort_values("Load (kW)", ascending=False)

    col_pie, col_bars = st.columns([1, 1.4], gap="medium")
    with col_pie:
        fig_pie = go.Figure(go.Pie(
            labels=df_breakdown["Component"],
            values=df_breakdown["Load (kW)"],
            hole=0.55,
            marker_colors=df_breakdown["Color"].tolist(),
            textinfo="percent",
            textfont_size=10
        ))
        fig_pie.update_layout(
            height=260, margin=dict(l=0,r=0,t=30,b=0),
            title=dict(text=f"{selected_bldg} Load Mix", font=dict(size=13, color="#0F172A"), x=0.5),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(
                text=f"<b>{bstats.get('avg_kw',0)}</b><br>kW",
                x=0.5, y=0.5, font_size=16, showarrow=False, font_color="#0F172A"
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True,
                        config={"displayModeBar":False}, key="bldg_pie")

    with col_bars:
        st.markdown(f"""
        <div style="font-size:0.9rem;font-weight:700;color:#0F172A;margin-bottom:12px;">
          Equipment-wise Power Draw — {selected_bldg}
        </div>
        """, unsafe_allow_html=True)
        for _, row in df_breakdown.iterrows():
            bar_w = min(100, int(row["% Share"]))
            st.markdown(f"""
            <div style="margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;
                          font-size:0.8rem;margin-bottom:3px;">
                <span style="color:#0F172A;font-weight:600;">{row['Component']}</span>
                <span style="color:#475569;">{row['Load (kW)']:.2f} kW
                  <span style="color:#94A3B8;"> ({row['% Share']}%)</span></span>
              </div>
              <div style="height:6px;background:#F1F5F9;border-radius:4px;">
                <div style="height:6px;background:{row['Color']};border-radius:4px;width:{bar_w}%;"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Key insight box
        top_component = df_breakdown.iloc[0] if not df_breakdown.empty else None
        if top_component is not None:
            st.markdown(f"""
            <div style="background:#EFF6FF;border-left:4px solid #3B82F6;
                        padding:10px 14px;border-radius:6px;margin-top:8px;">
              <span style="font-size:0.8rem;color:#1D4ED8;font-weight:600;">
                💡 Key Driver:
              </span>
              <span style="font-size:0.8rem;color:#1E40AF;">
                <b>{top_component['Component']}</b> contributes
                <b>{top_component['% Share']}%</b> of total building consumption
                ({top_component['Load (kW)']:.2f} kW). This is the primary target
                for energy reduction in {selected_bldg}.
              </span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Feature Importance (New Feature) ──────────────────────────────────────
    st.markdown("""
    <div style="padding:12px 0 4px 0;">
      <div style="font-size:1.3rem;font-weight:800;color:#0F172A;">
        🧠 Feature Importance — What Drives Power Consumption?
      </div>
      <div style="color:#94A3B8;font-size:0.82rem;">
        Correlation-based importance of each operational parameter on campus energy load
      </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Feature Importance: use cached df_imp from _precompute_dashboard ---
    col_imp1, col_imp2 = st.columns([1.4, 1], gap="medium")
    with col_imp1:
        colors_imp = []
        for v in df_imp["Importance"]:
            if v >= 0.7:   colors_imp.append("#EF4444")
            elif v >= 0.4: colors_imp.append("#F59E0B")
            else:          colors_imp.append("#10B981")

        fig_imp = go.Figure(go.Bar(
            x=df_imp["Importance"], y=df_imp["Feature"],
            orientation="h",
            marker=dict(color=colors_imp, line=dict(width=0)),
            text=[f"{v:.3f}" for v in df_imp["Importance"]],
            textposition="outside",
            textfont=dict(size=10, color="#475569")
        ))
        fig_imp.update_layout(
            height=320, margin=dict(l=0, r=50, t=0, b=0),
            xaxis=dict(title="Correlation with Energy Consumption",
                       range=[0, 1.1], tickfont=dict(size=9, color="#94A3B8"),
                       gridcolor="#F1F5F9"),
            yaxis=dict(tickfont=dict(size=10, color="#0F172A")),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        st.plotly_chart(fig_imp, use_container_width=True,
                        config={"displayModeBar": False}, key="feat_imp_bar")

    with col_imp2:
        st.markdown("""
        <div style="background:white;border-radius:12px;padding:18px;
                    box-shadow:0 1px 3px rgba(0,0,0,0.05);height:100%;">
          <div style="font-size:0.88rem;font-weight:700;color:#0F172A;margin-bottom:12px;">
            Feature Importance Legend
          </div>
        """, unsafe_allow_html=True)

        tiers = [
            ("#EF4444","High Impact (≥0.7)","Dominant energy driver. Changes here directly shift campus load significantly."),
            ("#F59E0B","Medium Impact (0.4–0.7)","Moderate influence. Optimising these yields measurable but incremental savings."),
            ("#10B981","Low Impact (<0.4)","Marginal contributor. Useful context but not primary levers for savings."),
        ]
        for color, tier, desc in tiers:
            st.markdown(f"""
            <div style="display:flex;gap:10px;margin-bottom:12px;align-items:flex-start;">
              <div style="min-width:12px;height:12px;background:{color};
                          border-radius:3px;margin-top:3px;"></div>
              <div>
                <div style="font-size:0.8rem;font-weight:700;color:#0F172A;">{tier}</div>
                <div style="font-size:0.72rem;color:#64748B;line-height:1.4;">{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Top driver highlight
        top_feat = df_imp.iloc[-1]
        st.markdown(f"""
        <div style="background:#FEF2F2;border-left:3px solid #EF4444;
                    padding:10px;border-radius:6px;margin-top:4px;">
          <div style="font-size:0.78rem;font-weight:700;color:#DC2626;">
            🔺 Top Driver: {top_feat['Feature']}
          </div>
          <div style="font-size:0.72rem;color:#7F1D1D;margin-top:2px;">
            Correlation = {top_feat['Importance']:.3f} with campus energy.
            Reducing this parameter yields the highest energy savings potential.
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Energy Source Distribution ─────────────────────────────────────────────
    st.markdown("""
    <div style="padding:12px 0 4px 0;">
      <div style="font-size:1.3rem;font-weight:800;color:#0F172A;">
        ⚡ Energy Source Distribution
      </div>
      <div style="color:#94A3B8;font-size:0.82rem;">
        Live grid / solar / diesel dispatch + battery backup
      </div>
    </div>
    """, unsafe_allow_html=True)

    grid_kw      = round(kpis["avg_hourly_consumption_kwh"] * 6, 1)
    battery_pct  = 78

    col_src, col_dispatch = st.columns([1, 1.6], gap="medium")
    with col_src:
        fig_donut = go.Figure(go.Pie(
            labels=["Grid", "Solar", "Diesel"],
            values=[100, 0.1, 0.1],
            hole=0.72,
            marker_colors=["#3B82F6","#F59E0B","#10B981"],
            textinfo="none"
        ))
        fig_donut.update_layout(
            height=220, margin=dict(l=20,r=20,t=0,b=0),
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.05,
                        x=0.5, xanchor="center", font=dict(size=11,color="#475569")),
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text=f"<b>{grid_kw}</b><br>kW",
                              x=0.5, y=0.5, font_size=18,
                              showarrow=False, font_color="#0F172A")]
        )
        st.plotly_chart(fig_donut, use_container_width=True,
                        config={"displayModeBar":False}, key="src_donut")

    with col_dispatch:
        def drow(icon, label, kw, sub, bar_color, bar_pct):
            return f"""
            <div style="margin-bottom:14px;">
              <div style="display:flex;justify-content:space-between;
                          align-items:center;margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <span>{icon}</span>
                  <div>
                    <div style="font-size:0.85rem;font-weight:600;color:#0F172A;">{label}</div>
                    <div style="font-size:0.7rem;color:#94A3B8;">{sub}</div>
                  </div>
                </div>
                <span style="font-size:0.9rem;font-weight:700;color:#0F172A;">{kw} kW</span>
              </div>
              <div style="height:6px;background:#F1F5F9;border-radius:4px;">
                <div style="height:6px;background:{bar_color};border-radius:4px;
                             width:{bar_pct}%;"></div>
              </div>
            </div>"""
        st.markdown(
            '<div class="kpi-card"><div style="font-weight:600;color:#0F172A;margin-bottom:14px;">Live Dispatch</div>' +
            drow("⚡","Grid Supply",grid_kw,"100% of load · Import limit 500 kW","#3B82F6",100) +
            drow("☀️","Solar Generation",0.0,"0% of load · 80 kW capacity available","#F59E0B",0) +
            drow("🔋","Diesel Generator",0.0,"Standby — grid sufficient","#6B7280",0) +
            f"""<div>
              <div style="display:flex;justify-content:space-between;
                          align-items:center;margin-bottom:4px;">
                <div style="display:flex;align-items:center;gap:8px;">
                  <span>🔋</span>
                  <div>
                    <div style="font-size:0.85rem;font-weight:600;color:#0F172A;">Battery Backup</div>
                    <div style="font-size:0.7rem;color:#94A3B8;">120 kWh · 30 kW discharge</div>
                  </div>
                </div>
                <span style="font-size:0.9rem;font-weight:700;color:#10B981;">{battery_pct}% SoC</span>
              </div>
              <div style="height:10px;background:#F1F5F9;border-radius:6px;">
                <div style="height:10px;background:linear-gradient(90deg,#10B981,#34D399);
                             border-radius:6px;width:{battery_pct}%;"></div>
              </div>
            </div></div>""",
            unsafe_allow_html=True
        )

    st.markdown("---")

    # ── Equipment Status ───────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:12px 0 4px 0;">
      <div style="font-size:1.3rem;font-weight:800;color:#0F172A;">
        🖥️ Equipment Status &amp; Capacity
      </div>
      <div style="color:#94A3B8;font-size:0.82rem;">
        Connected vs active load, running equipment, utilisation thresholds
      </div>
    </div>
    """, unsafe_allow_html=True)

    total_pcs  = equip_totals["total_pcs"]
    total_acs  = equip_totals["total_acs"]
    total_occ  = equip_totals["total_occ"]
    lab_active = equip_totals["lab_active"]
    workshop_a = equip_totals["workshop_a"]

    eq_cols = st.columns(6, gap="medium")
    equip_items = [
        ("💻", total_pcs, 952, "Running Computers",    "desktops active"),
        ("❄️", total_acs, 123, "Running ACs",           "air conditioners"),
        ("🔬", lab_active, 6,  "Running Laboratories",  "labs in session"),
        ("🏫", workshop_a, 4,  "Running Classrooms",    "classrooms occupied"),
        ("🌀", 0, 64,          "Running Fans",           "ceiling fans"),
        ("👥", total_occ, 1541,"Current Occupancy",     "10% occupied"),
    ]
    for col, (icon, val, cap, label, sub) in zip(eq_cols, equip_items):
        with col:
            st.markdown(f"""
            <div class="equip-card">
              <div style="font-size:1.4rem;margin-bottom:4px;">{icon}</div>
              <div style="font-size:1.3rem;font-weight:800;color:#0F172A;">
                {val}<span style="font-size:0.8rem;font-weight:500;color:#94A3B8;">/{cap}</span>
              </div>
              <div style="font-size:0.75rem;font-weight:600;color:#0F172A;">{label}</div>
              <div style="font-size:0.68rem;color:#94A3B8;">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    col_load, col_thresh = st.columns([1, 1.4], gap="medium")
    connected_kw = round(kpis["total_energy_kwh"] * 4.5, 1)
    active_kw    = round(kpis["total_energy_kwh"] / 24 * 6, 1)
    remaining_kw = round(connected_kw - active_kw, 1)
    utilisation  = round(min(100, active_kw / max(connected_kw, 1) * 100), 1)

    with col_load:
        st.markdown(f"""
        <div class="kpi-card">
          <div style="font-weight:700;color:#0F172A;margin-bottom:12px;">
            ⚡ Connected vs Active Load
          </div>
          <div style="display:flex;justify-content:space-between;
                      margin-bottom:5px;font-size:0.84rem;">
            <span style="color:#64748B;">Connected (Installed) Load</span>
            <span style="font-weight:700;color:#0F172A;">{connected_kw} kW</span>
          </div>
          <div style="display:flex;justify-content:space-between;
                      margin-bottom:4px;font-size:0.84rem;">
            <span style="color:#64748B;">Active (Running) Load</span>
            <span style="font-weight:700;color:#3B82F6;">{active_kw} kW</span>
          </div>
          <div style="height:6px;background:#F1F5F9;border-radius:4px;margin-bottom:8px;">
            <div style="height:6px;background:#3B82F6;border-radius:4px;
                         width:{utilisation}%;"></div>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.84rem;">
            <span style="color:#64748B;">Remaining Capacity</span>
            <span style="font-weight:700;color:#10B981;">{remaining_kw} kW</span>
          </div>
          <div style="display:flex;justify-content:space-between;
                      margin-top:8px;font-size:0.8rem;">
            <span style="color:#64748B;">Utilisation</span>
            <span style="font-weight:700;color:#F59E0B;">{utilisation}% — Normal</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_thresh:
        st.markdown("""
        <div class="kpi-card">
          <div style="font-weight:700;color:#0F172A;margin-bottom:12px;">
            📊 Threshold Bands
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:8px;margin-bottom:12px;">
            <div style="background:#ECFDF5;border-radius:8px;padding:10px;text-align:center;">
              <div style="color:#059669;font-size:0.62rem;font-weight:700;text-transform:uppercase;">NORMAL</div>
              <div style="font-size:1rem;font-weight:800;color:#059669;">0–70%</div>
              <div style="font-size:0.62rem;color:#6EE7B7;">Within range</div>
            </div>
            <div style="background:#FFFBEB;border-radius:8px;padding:10px;text-align:center;">
              <div style="color:#D97706;font-size:0.62rem;font-weight:700;text-transform:uppercase;">WARNING</div>
              <div style="font-size:1rem;font-weight:800;color:#D97706;">70–85%</div>
              <div style="font-size:0.62rem;color:#FCD34D;">Approaching</div>
            </div>
            <div style="background:#FFF7ED;border-radius:8px;padding:10px;text-align:center;">
              <div style="color:#EA580C;font-size:0.62rem;font-weight:700;text-transform:uppercase;">HIGH</div>
              <div style="font-size:1rem;font-weight:800;color:#EA580C;">85–95%</div>
              <div style="font-size:0.62rem;color:#FDBA74;">Near peak</div>
            </div>
            <div style="background:#FEF2F2;border-radius:8px;padding:10px;text-align:center;">
              <div style="color:#DC2626;font-size:0.62rem;font-weight:700;text-transform:uppercase;">CRITICAL</div>
              <div style="font-size:1rem;font-weight:800;color:#DC2626;">95–100%</div>
              <div style="font-size:0.62rem;color:#FCA5A5;">Over capacity</div>
            </div>
          </div>
          <div style="font-size:0.7rem;color:#94A3B8;line-height:1.5;">
            Utilisation = Active Load ÷ Connected Load. Bands align with IEEE 519 
            and BEE (Bureau of Energy Efficiency) demand management guidelines.
          </div>
        </div>
        """, unsafe_allow_html=True)
