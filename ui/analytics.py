"""
Energy Analytics Page — Redesigned to match reference UI.
Sections: Live Campus Load Gauge · Live Energy Meter · Building Comparison
          Energy Distribution Donut · Hourly Consumption Trend · Campus Load Timeline
          Top Energy Consumers · Building-wise Heat Map
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from services.data_service import DataService
from services.analytics_service import AnalyticsService

@st.cache_data(ttl=600, show_spinner=False)
def _precompute_analytics(csv_path: str):
    from services.data_service import _load_and_process_csv
    df = _load_and_process_csv(csv_path)
    
    # 1. Building Averages
    bldg_avg = df.groupby("Building")["Energy Consumption"].mean().reset_index()
    bldg_avg.columns = ["Building", "Avg_kW"]
    bldg_avg = bldg_avg.sort_values("Avg_kW", ascending=True)
    
    # 2. Hourly Totals
    hourly_total = df.groupby("Hour")["Energy Consumption"].sum().reset_index()
    hourly_total.columns = ["Hour", "Total_kW"]
    
    total_live_kw = round(df["Energy Consumption"].mean() * df["Building"].nunique(), 1)
    
    # 3. Component distribution totals
    dist_totals = {
        "hvac": round(df["HVAC Load"].sum(), 1),
        "light": round(df["Lighting Load"].sum(), 1),
        "lab": round(df["Laboratory Usage"].sum(), 1),
        "ws": round(df["Workshop Usage"].sum(), 1),
        "equip": round(df["Equipment Usage"].sum(), 1),
        "coe": round(df["CoE Activity"].sum(), 1)
    }
    
    # 4. Hourly data per building for the timeline
    bldg_hourly = {}
    for b in df["Building"].unique():
        bdf = df[df["Building"]==b].groupby("Hour")["Energy Consumption"].mean().reset_index()
        bldg_hourly[b] = {"Hour": bdf["Hour"].tolist(), "Energy Consumption": bdf["Energy Consumption"].tolist()}
        
    # 5. Top Rows (Floor wise mean)
    top_rows = df.groupby(["Building","Floor"])["Energy Consumption"].mean().reset_index()
    
    # 6. Correlation Matrix
    corr_cols = [
        "Temperature", "Humidity", "Occupancy", "Running Computers",
        "Running ACs", "Energy Consumption", "Lighting Load", "HVAC Load"
    ]
    # Filter columns that actually exist
    valid_cols = [c for c in corr_cols if c in df.columns]
    corr_df = df[valid_cols].corr()
    
    return bldg_avg, hourly_total, total_live_kw, dist_totals, bldg_hourly, top_rows, corr_df

def _hex_to_rgba(hex_color: str, alpha: float = 0.7) -> str:
    """Converts #RRGGBB to rgba(r,g,b,a) for valid Plotly fillcolor."""
    try:
        r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        return f"rgba({r},{g},{b},{alpha})"
    except Exception:
        return f"rgba(5,150,105,{alpha})"

def render_analytics() -> None:
    data_svc  = DataService()
    analytics  = AnalyticsService()
    
    # Pre-compute all Pandas operations once per session
    bldg_avg, hourly_total, total_live_kw, dist_totals, bldg_hourly, top_rows, corr_df = _precompute_analytics(data_svc.csv_path)
    
    # Load dataset for raw point rendering (cached, O(1))
    df = data_svc.load_dataset()

    # ── Section Header ────────────────────────────────────────────────────────


    SHORT = {
        "Academic Block A": "Block A", "Academic Block B": "Block B",
        "Academic Block C": "Block C", "Academic Block D": "Block D",
        "Workshop Building": "Workshop", "Centre of Excellence": "CoE"
    }
    bldg_avg["Short"] = bldg_avg["Building"].map(SHORT)
    campus_max_kw = 445  # Reference capacity

    # Energy distribution by type (derived from dist_totals)
    hvac_total  = dist_totals["hvac"]
    light_total = dist_totals["light"]
    lab_total   = dist_totals["lab"]
    ws_total    = dist_totals["ws"]
    equip_total = dist_totals["equip"]
    coe_total   = dist_totals["coe"]

    # ── Row 1: Gauge · Energy Meter · Building Bar · Distribution Donut ───────
    c1, c2, c3, c4 = st.columns(4, gap="medium")

    with c1:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:8px;">
            🎯 Live Campus Load Gauge
        </div>""", unsafe_allow_html=True)
        gauge_pct = min(100, round(total_live_kw / campus_max_kw * 100))
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_live_kw,
            number={"suffix": " kW", "font": {"size": 20, "color": "#0F172A", "family": "Inter"}},
            gauge={
                "axis": {"range": [0, campus_max_kw],
                         "tickfont": {"size": 9, "color": "#94A3B8"},
                         "tickwidth": 1},
                "bar": {"color": "#059669", "thickness": 0.25},
                "bgcolor": "#F1F5F9",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, campus_max_kw*0.70], "color": "#ECFDF5"},
                    {"range": [campus_max_kw*0.70, campus_max_kw*0.85], "color": "#FFFBEB"},
                    {"range": [campus_max_kw*0.85, campus_max_kw], "color": "#FEF2F2"},
                ],
                "threshold": {"line": {"color": "#EF4444", "width": 2},
                              "thickness": 0.8, "value": campus_max_kw*0.85}
            }
        ))
        fig_gauge.update_layout(
            height=180, margin=dict(l=10, r=10, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)", font_family="Inter"
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False}, key="ana_gauge")
        st.markdown(f"""
        <div style="text-align:center;font-size:0.72rem;margin-top:-8px;">
            <span style="font-size:0.85rem;font-weight:700;color:#0F172A;">{total_live_kw} kW</span>
            <span style="color:#94A3B8;"> Total Demand</span><br>
            <span style="background:#ECFDF5;color:#059669;font-size:0.7rem;padding:2px 8px;
                         border-radius:10px;font-weight:600;">Normal · {gauge_pct}%</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:8px;">
            ⚡ Live Energy Meter
            <span style="float:right;width:8px;height:8px;background:#10B981;
                          border-radius:50%;display:inline-block;margin-top:3px;"></span>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-size:2.5rem;font-weight:800;color:#0F172A;
                    text-align:center;margin:12px 0 4px 0;">
            {total_live_kw}<span style="font-size:1rem;color:#94A3B8;"> kW</span>
        </div>""", unsafe_allow_html=True)

        # Meter bar
        bar_vals = [2,3,5,8,10,12,10,12,15,18,20,22,20,18,16,15,14,12,10,8,5,4,3,2]
        bar_clrs = ["#059669" if v < 15 else "#F59E0B" for v in bar_vals]
        fig_meter = go.Figure(go.Bar(
            x=list(range(24)), y=bar_vals,
            marker_color=bar_clrs, width=0.7
        ))
        fig_meter.add_hline(y=15, line_dash="dot", line_color="#10B981",
                            annotation_text="Normal", annotation_font_size=9)
        fig_meter.update_layout(
            height=100, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        st.plotly_chart(fig_meter, use_container_width=True, config={"displayModeBar": False}, key="ana_meter")
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;
                    font-size:0.72rem;color:#94A3B8;margin-top:-4px;">
            <span>0 kW</span>
            <span style="color:#10B981;font-weight:600;">Normal</span>
            <span>{campus_max_kw} kW</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
            <span style="font-size:0.82rem;font-weight:600;color:#475569;">📊 Building Comparison</span>
            <span style="font-size:0.7rem;color:#94A3B8;">Current kW</span>
        </div>""", unsafe_allow_html=True)
        fig_bldg = go.Figure(go.Bar(
            x=bldg_avg["Avg_kW"], y=bldg_avg["Short"],
            orientation="h",
            marker=dict(
                color=bldg_avg["Avg_kW"],
                colorscale=[[0,"#A7F3D0"],[0.5,"#059669"],[1.0,"#047857"]],
                showscale=False
            ),
            text=[f"{v:.1f}" for v in bldg_avg["Avg_kW"]],
            textposition="outside",
            textfont=dict(size=10, color="#475569")
        ))
        fig_bldg.update_layout(
            height=220, margin=dict(l=0,r=30,t=0,b=0),
            xaxis=dict(visible=False),
            yaxis=dict(tickfont=dict(size=10, color="#475569")),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        st.plotly_chart(fig_bldg, use_container_width=True, config={"displayModeBar": False}, key="ana_bldg_bar")
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:8px;">
            🥧 Energy Distribution
        </div>""", unsafe_allow_html=True)
        dist_labels = ["HVAC","Lighting","Computer Labs","Admin Offices","Classrooms","Research Labs","Common Areas"]
        dist_vals   = [hvac_total, light_total, lab_total, equip_total, ws_total, coe_total, max(1, lab_total*0.1)]
        fig_dist = go.Figure(go.Pie(
            labels=dist_labels, values=dist_vals,
            hole=0.0, textinfo="percent",
            textfont_size=9,
            marker_colors=["#059669","#F59E0B","#10B981","#8B5CF6","#06B6D4","#EF4444","#94A3B8"]
        ))
        fig_dist.update_layout(
            height=220, margin=dict(l=0,r=0,t=0,b=0),
            showlegend=True,
            legend=dict(font=dict(size=8, color="#475569"),
                        orientation="v", x=1.0, y=0.5),
            paper_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_dist, use_container_width=True, config={"displayModeBar": False}, key="ana_dist_pie")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Row 2: Hourly Trend · Campus Load Timeline · Top Consumers · Heatmap ─
    c5, c6, c7, c8 = st.columns(4, gap="medium")

    with c5:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:0.82rem;font-weight:600;color:#475569;">📉 Hourly Consumption Trend</span>
            <span style="font-size:0.7rem;color:#94A3B8;">Today · 24h profile</span>
        </div>""", unsafe_allow_html=True)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=hourly_total["Hour"], y=hourly_total["Total_kW"],
            mode="lines", name="Total Campus",
            line=dict(color="#059669", width=2.5, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(5,150,105,0.1)"
        ))
        fig_trend.update_layout(
            height=200, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(tickfont=dict(size=8,color="#94A3B8"),
                       gridcolor="#F1F5F9", showgrid=True),
            yaxis=dict(tickfont=dict(size=8,color="#94A3B8"),
                       gridcolor="#F1F5F9", showgrid=True),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False
        )
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False}, key="ana_trend")
        st.markdown('</div>', unsafe_allow_html=True)

    with c6:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:0.82rem;font-weight:600;color:#475569;">📊 Campus Load Timeline</span>
            <span style="font-size:0.7rem;color:#94A3B8;">Stacked building load</span>
        </div>""", unsafe_allow_html=True)

        colors_map = {
            "Academic Block A": "#059669",
            "Academic Block B": "#10B981",
            "Academic Block C": "#F59E0B",
            "Academic Block D": "#8B5CF6",
            "Workshop Building": "#EF4444",
            "Centre of Excellence": "#06B6D4",
        }
        fig_stack = go.Figure()
        bldg_list = list(df["Building"].unique())
        for bldg in bldg_list:
            bdf = bldg_hourly.get(bldg)
            if not bdf: continue
            fill_mode = "tozeroy" if bldg == bldg_list[0] else "tonexty"
            fill_rgba = _hex_to_rgba(colors_map.get(bldg, "#059669"), 0.65)
            fig_stack.add_trace(go.Scatter(
                x=bdf["Hour"], y=bdf["Energy Consumption"],
                mode="lines", name=SHORT.get(bldg, bldg),
                line=dict(width=0),
                fill=fill_mode,
                fillcolor=fill_rgba,
                stackgroup="one"
            ))
        fig_stack.update_layout(
            height=200, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(tickfont=dict(size=8,color="#94A3B8"),gridcolor="#F1F5F9"),
            yaxis=dict(tickfont=dict(size=8,color="#94A3B8"),gridcolor="#F1F5F9"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(size=7,color="#475569"),
                        orientation="h", y=-0.15, x=0, xanchor="left"),
            showlegend=True
        )
        st.plotly_chart(fig_stack, use_container_width=True, config={"displayModeBar": False}, key="ana_stack")
        st.markdown('</div>', unsafe_allow_html=True)

    with c7:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <span style="font-size:0.82rem;font-weight:600;color:#475569;">🏆 Top Energy Consumers</span>
            <span style="font-size:0.7rem;color:#94A3B8;">By floor</span>
        </div>""", unsafe_allow_html=True)

        # Per-building top consumers by floor average
        # use precomputed top_rows
        top_rows.columns = ["Building","Floor","Avg_kW"]
        top_rows["Label"] = top_rows.apply(
            lambda r: f"{SHORT.get(r['Building'],r['Building'])} · Floor {r['Floor']}", axis=1
        )
        top_rows = top_rows.sort_values("Avg_kW", ascending=False).head(8)

        for i, row in top_rows.iterrows():
            bar_pct = round(row["Avg_kW"] / top_rows["Avg_kW"].max() * 100)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                <span style="font-size:0.72rem;color:#94A3B8;width:16px;text-align:right;">
                    {list(top_rows.index).index(i)+1}
                </span>
                <div style="flex:1;">
                    <div style="font-size:0.75rem;color:#0F172A;font-weight:500;margin-bottom:2px;">
                        {row['Label']}
                    </div>
                    <div style="height:4px;background:#F1F5F9;border-radius:4px;">
                        <div style="height:4px;background:#059669;border-radius:4px;width:{bar_pct}%;"></div>
                    </div>
                </div>
                <span style="font-size:0.78rem;font-weight:700;color:#0F172A;min-width:48px;text-align:right;">
                    {row['Avg_kW']:.1f} kW
                </span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c8:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:0.82rem;font-weight:600;color:#475569;">🗺️ Building-wise Heat Map</span>
            <span style="font-size:0.7rem;color:#94A3B8;">Load intensity by hour</span>
        </div>""", unsafe_allow_html=True)

        # Pivot: rows=buildings, cols=hours
        heat_pivot = df.pivot_table(
            index="Building", columns="Hour",
            values="Energy Consumption", aggfunc="mean"
        ).fillna(0)
        heat_pivot.index = [SHORT.get(b,b) for b in heat_pivot.index]

        fig_heat = go.Figure(go.Heatmap(
            z=heat_pivot.values,
            x=[str(h) for h in heat_pivot.columns],
            y=list(heat_pivot.index),
            colorscale=[
                [0.0,  "#ECFDF5"],
                [0.35, "#6EE7B7"],
                [0.65, "#F59E0B"],
                [1.0,  "#EF4444"],
            ],
            showscale=True,
            colorbar=dict(
                thickness=8, len=0.8,
                tickfont=dict(size=8, color="#94A3B8"),
                title=dict(text="kW", font=dict(size=9, color="#94A3B8"))
            )
        ))
        fig_heat.update_layout(
            height=220, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(tickfont=dict(size=7,color="#94A3B8"),
                       title=dict(text="Hour",font=dict(size=9,color="#94A3B8"))),
            yaxis=dict(tickfont=dict(size=8,color="#94A3B8")),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False}, key="ana_heatmap")
        st.markdown("""
        <div style="display:flex;justify-content:space-between;font-size:0.7rem;
                    color:#94A3B8;margin-top:-4px;">
            <span>Low</span>
            <span>High</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 3: Detailed Correlation & Weather Impact ───────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class="section-header">
        <div class="section-icon" style="background:#F5F3FF;">🧮</div>
        <div>
            <div style="font-size:1.1rem;font-weight:700;color:#0F172A;">Detailed Correlation & Weather Analysis</div>
            <div style="color:#94A3B8;font-size:0.82rem;">Environmental factors vs campus power draw</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_corr, col_wea = st.columns(2, gap="medium")

    with col_corr:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        # corr_df is already precomputed from cached function
        fig_corr = px.imshow(
            corr_df, color_continuous_scale="RdBu",
            zmin=-1, zmax=1, text_auto=".2f"
        )
        fig_corr.update_layout(
            height=320, margin=dict(l=0,r=0,t=0,b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(thickness=10,
                                    tickfont=dict(size=9,color="#94A3B8"))
        )
        st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar":False}, key="ana_corr")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_wea:
        st.markdown('<div class="kpi-card">', unsafe_allow_html=True)
        # Use graph_objects scatter to avoid statsmodels dependency
        color_map_list = ["#059669","#10B981","#F59E0B","#8B5CF6","#EF4444","#06B6D4"]
        fig_scat = go.Figure()
        for i, bldg in enumerate(df["Building"].unique()):
            bdf_s = df[df["Building"]==bldg]
            clr = color_map_list[i % len(color_map_list)]
            fig_scat.add_trace(go.Scatter(
                x=bdf_s["Temperature"], y=bdf_s["Energy Consumption"],
                mode="markers", name=SHORT.get(bldg, bldg),
                marker=dict(color=clr, size=5, opacity=0.7)
            ))
        fig_scat.update_layout(
            height=320, margin=dict(l=0,r=0,t=0,b=0),
            xaxis=dict(title="Temp (°C)", tickfont=dict(size=9,color="#94A3B8"),
                       gridcolor="#F1F5F9"),
            yaxis=dict(title="Load (kW)", tickfont=dict(size=9,color="#94A3B8"),
                       gridcolor="#F1F5F9"),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FAFAFA",
            legend=dict(font=dict(size=9,color="#475569"),
                        orientation="h", y=-0.15, x=0, xanchor="left")
        )
        st.plotly_chart(fig_scat, use_container_width=True,
                        config={"displayModeBar":False}, key="ana_scatter")
        st.markdown('</div>', unsafe_allow_html=True)
