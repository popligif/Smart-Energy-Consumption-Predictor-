import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math

try:
    from services.forecast_service import (
        predict_next_hour,
        predict_next_24h,
        predict_next_7days,
        predict_next_30days,
        get_model_metrics,
        get_historical_hourly
    )
except ImportError:
    pass # we handle it in the function if missing

def render_forecasting():
    
    with st.spinner('Training forecast model...'):
        try:
            next_hour = predict_next_hour()
            next_24h = predict_next_24h()
            next_7d = predict_next_7days()
            next_30d = predict_next_30days()
            metrics = get_model_metrics()
            historical = get_historical_hourly()
        except Exception as e:
            st.error(f"Error loading forecast data: {e}")
            return
            
    avg_hist_kw = historical['y'].mean() if (historical is not None and not historical.empty and 'y' in historical.columns) else 100
    pred_kw = next_hour.get('predicted_kw', 0)
    ratio = pred_kw / avg_hist_kw if avg_hist_kw else 1
    
    if ratio < 0.8:
        status_color = "#10B981"
        status_text = "Normal"
    elif ratio > 1.2:
        status_color = "#EF4444"
        status_text = "Critical"
    else:
        status_color = "#F59E0B"
        status_text = "Elevated"

    mae = metrics.get('mae', 0)
    mape = metrics.get('mape', 0)
    lower_kw = next_hour.get('lower_kw', pred_kw * 0.9)
    upper_kw = next_hour.get('upper_kw', pred_kw * 1.1)

    # ROW 1 - Hero Prediction Panel
    st.markdown(f"""
    <style>
    @keyframes pulse-ring {{
        0% {{ box-shadow: 0 0 0 0 {status_color}80; }}
        70% {{ box-shadow: 0 0 0 15px transparent; }}
        100% {{ box-shadow: 0 0 0 0 transparent; }}
    }}
    .hero-container {{ display: flex; gap: 1rem; margin-bottom: 1.5rem; }}
    .hero-card {{ flex: 1; background: white; border-radius: 0.75rem; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; font-family: 'Inter', sans-serif; }}
    .glow-ring {{ border-radius: 50%; padding: 2rem; border: 4px solid {status_color}; animation: pulse-ring 2s infinite; margin-bottom: 1rem; }}
    .glow-num {{ font-size: 2.5rem; font-weight: 700; color: #0F172A; line-height: 1; }}
    .status-chip {{ background-color: {status_color}20; color: {status_color}; padding: 0.25rem 0.75rem; border-radius: 9999px; font-weight: 600; font-size: 0.875rem; margin-top: 0.5rem; }}
    .metrics-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; width: 100%; }}
    .metric-box {{ background: #F1F5F9; border-radius: 0.5rem; padding: 1rem; text-align: left; }}
    .metric-val {{ font-size: 1.5rem; font-weight: 700; color: #0F172A; }}
    .metric-label {{ font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase; margin-top: 0.25rem; display: flex; justify-content: space-between; align-items: center; }}
    .badge-violet {{ background: #8B5CF620; color: #8B5CF6; padding: 0.15rem 0.4rem; border-radius: 0.25rem; font-size: 0.65rem; }}
    .badge-sky {{ background: #06B6D420; color: #06B6D4; padding: 0.15rem 0.4rem; border-radius: 0.25rem; font-size: 0.65rem; }}
    </style>
    <div class="hero-container">
        <div class="hero-card">
            <h3 style="color: #64748B; margin: 0 0 1rem 0; font-size: 1.1rem; font-weight: 600;">Next Hour Prediction</h3>
            <div class="glow-ring">
                <div class="glow-num">{pred_kw:.1f} <span style="font-size:1.25rem; font-weight:500;">kW</span></div>
            </div>
            <div style="color:#64748B; font-size:0.9rem;">Confidence: {lower_kw:.1f} - {upper_kw:.1f} kW (±{abs(pred_kw - lower_kw):.1f} kW)</div>
            <div class="status-chip">{status_text}</div>
        </div>
        <div class="hero-card">
            <h3 style="color: #64748B; margin: 0 0 1.5rem 0; font-size: 1.1rem; font-weight: 600;">Model Accuracy</h3>
            <div class="metrics-grid">
                <div class="metric-box">
                    <div class="metric-val">{mae:.2f}</div>
                    <div class="metric-label">MAE <span class="badge-violet">Excellent</span></div>
                </div>
                <div class="metric-box">
                    <div class="metric-val">{mape:.1f}%</div>
                    <div class="metric-label">MAPE <span class="badge-sky">High Confidence</span></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ROW 2 - 24-Hour Forecast Chart
    st.subheader("24-Hour Forecast")
    
    fig_24 = go.Figure()
    # Confidence Band
    fig_24.add_trace(go.Scatter(
        x=next_24h['timestamp'].tolist() + next_24h['timestamp'].tolist()[::-1],
        y=next_24h['upper_kw'].tolist() + next_24h['lower_kw'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(16, 185, 129, 0.2)', # Emerald transparent
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo="skip",
        showlegend=True,
        name='Confidence Interval'
    ))
    # Prediction Line
    fig_24.add_trace(go.Scatter(
        x=next_24h['timestamp'],
        y=next_24h['predicted_kw'],
        mode='lines',
        line=dict(color='#10B981', width=3), # Emerald
        name='Predicted kW'
    ))
    fig_24.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#E2E8F0', zeroline=False),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_24, use_container_width=True, key='chart_24h')

    # ROW 3
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("7-Day Forecast")
        fig_7 = go.Figure()
        
        avg_7d = next_7d['daily_kwh'].mean() if not next_7d.empty else 1
        colors = []
        for val in next_7d['daily_kwh']:
            r = val / avg_7d
            if r < 0.9: colors.append("#10B981") # Green
            elif r > 1.1: colors.append("#EF4444") # Red
            else: colors.append("#F59E0B") # Amber
            
        fig_7.add_trace(go.Bar(
            x=next_7d['date'],
            y=next_7d['daily_kwh'],
            marker_color=colors,
            name='Daily kWh'
        ))
        fig_7.update_layout(
            margin=dict(l=0, r=0, t=20, b=0),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#E2E8F0'),
            showlegend=False
        )
        st.plotly_chart(fig_7, use_container_width=True, key='chart_7d')

    with col2:
        st.subheader("30-Day Outlook")
        total_kwh = next_30d['daily_kwh'].sum() if not next_30d.empty else 0
        avg_kwh = next_30d['daily_kwh'].mean() if not next_30d.empty else 0
        peak_kwh = next_30d['daily_kwh'].max() if not next_30d.empty else 0
        low_kwh = next_30d['daily_kwh'].min() if not next_30d.empty else 0
        
        st.markdown(f"""
        <div style="background: white; border-radius: 0.75rem; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); font-family: 'Inter', sans-serif; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h4 style="margin: 0; color: #0F172A; font-size: 1rem; font-weight: 600;">Summary Metrics</h4>
                <span style="background: #F59E0B20; color: #F59E0B; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600;">⚠️ Indicative</span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div style="background: #F1F5F9; padding: 1rem; border-radius: 0.5rem;">
                    <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Total Projected</div>
                    <div style="font-size: 1.125rem; font-weight: 700; color: #0F172A; margin-top: 0.25rem;">{total_kwh:,.0f} kWh</div>
                </div>
                <div style="background: #F1F5F9; padding: 1rem; border-radius: 0.5rem;">
                    <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Daily Average</div>
                    <div style="font-size: 1.125rem; font-weight: 700; color: #0F172A; margin-top: 0.25rem;">{avg_kwh:,.0f} kWh</div>
                </div>
                <div style="background: #F1F5F9; padding: 1rem; border-radius: 0.5rem;">
                    <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Peak Day</div>
                    <div style="font-size: 1.125rem; font-weight: 700; color: #EF4444; margin-top: 0.25rem;">{peak_kwh:,.0f} kWh</div>
                </div>
                <div style="background: #F1F5F9; padding: 1rem; border-radius: 0.5rem;">
                    <div style="font-size: 0.75rem; color: #64748B; font-weight: 600; text-transform: uppercase;">Lowest Day</div>
                    <div style="font-size: 1.125rem; font-weight: 700; color: #10B981; margin-top: 0.25rem;">{low_kwh:,.0f} kWh</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ROW 4 - Model Info Panel
    st.markdown(f"""
    <div style="margin-top: 1.5rem; background: white; border-radius: 0.75rem; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); font-family: 'Inter', sans-serif;">
        <h4 style="margin: 0 0 1rem 0; color: #0F172A; font-size: 1rem; font-weight: 600;">Model Information</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; font-size: 0.875rem;">
            <div>
                <div style="margin-bottom: 0.75rem;"><strong style="color: #64748B;">Training Data Range:</strong> <span style="color: #0F172A; float: right;">1 July 2026 to 30 July 2026</span></div>
                <div style="margin-bottom: 0.75rem;"><strong style="color: #64748B;">Hourly Records:</strong> <span style="color: #0F172A; float: right;">{len(historical)}</span></div>
            </div>
            <div>
                <div style="margin-bottom: 0.75rem;"><strong style="color: #64748B;">Features Used:</strong> <span style="color: #0F172A; float: right;">Hour Sin/Cos, DoW Sin/Cos, Lags (1h, 24h, 168h), Rolling Mean</span></div>
                <div style="margin-bottom: 0.75rem;"><strong style="color: #64748B;">Model Type:</strong> <span style="color: #0F172A; float: right;">Gradient Boosting Regressor (sklearn)</span></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
