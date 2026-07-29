"""
UI component for Energy Analytics, comparative charts, heatmaps, and correlations (FR-3).
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from services.analytics_service import AnalyticsService
from services.data_service import DataService

def render_analytics() -> None:
    """Renders the Energy Analytics tab with interactive charts and filters."""
    st.header("⚡ Energy Command Centre (Analytics)")
    st.write("Perform detailed telemetry analysis, inspect correlations, and compare building load factors.")
    
    analytics_service = AnalyticsService()
    data_service = DataService()
    df = data_service.load_dataset()
    
    # 1. Filters Sidebar / Top Bar
    st.subheader("Filter Telemetry")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        buildings = sorted(df["Building"].unique().tolist())
        selected_buildings = st.multiselect("Select Buildings", options=buildings, default=buildings)
        
    with col_f2:
        floors = sorted(df["Floor"].unique().tolist())
        selected_floors = st.multiselect("Select Floors", options=floors, default=floors)
        
    with col_f3:
        load_types = sorted(df["Load Type"].unique().tolist())
        selected_load_types = st.multiselect("Select Load Type", options=load_types, default=load_types)
        
    # Apply filtering
    df_filtered = df[
        (df["Building"].isin(selected_buildings)) & 
        (df["Floor"].isin(selected_floors)) & 
        (df["Load Type"].isin(selected_load_types))
    ]
    
    if df_filtered.empty:
        st.warning("⚠️ No records match the selected filters. Please expand your filtering parameters.")
        return
        
    # 2. Tabs for Different Visualizations
    tab_trends, tab_comparison, tab_correlation, tab_weather = st.tabs([
        "📈 Hourly Trends", 
        "🏢 Building Comparison", 
        "🧮 Correlation Analysis", 
        "🌤️ Weather & Environmental Impact"
    ])
    
    with tab_trends:
        st.subheader("Hourly Energy Consumption Trends")
        # Line chart of energy consumption by Hour, colored by Building
        hourly_avg = df_filtered.groupby(["Hour", "Building"])["Energy Consumption"].mean().reset_index()
        fig_line = px.line(
            hourly_avg,
            x="Hour",
            y="Energy Consumption",
            color="Building",
            title="Average Energy Load (kW) Profile by Hour of Day",
            markers=True,
            labels={"Energy Consumption": "Power Load (kW)"}
        )
        fig_line.update_layout(xaxis=dict(tickmode="linear", tick0=0, dtick=1))
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Power Factor hourly trend
        st.subheader("Power Factor Hourly Profile")
        pf_avg = df_filtered.groupby(["Hour", "Building"])["Power Factor"].mean().reset_index()
        fig_pf = px.line(
            pf_avg,
            x="Hour",
            y="Power Factor",
            color="Building",
            title="Power Factor Trends (Threshold Benchmark: 0.90)",
            markers=True
        )
        # Add baseline threshold line
        fig_pf.add_hline(y=0.90, line_dash="dash", line_color="red", annotation_text="Efficiency Target (0.90)")
        fig_pf.update_layout(xaxis=dict(tickmode="linear", tick0=0, dtick=1))
        st.plotly_chart(fig_pf, use_container_width=True)

    with tab_comparison:
        st.subheader("Building Comparative Audits")
        # Bar chart comparing total consumption
        sum_data = df_filtered.groupby("Building").agg(
            Total_Energy=("Energy Consumption", "sum"),
            Total_Cost=("Dynamic Cost (INR)", "sum"),
            Avg_Occupancy=("Occupancy", "mean")
        ).reset_index()
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_bar_energy = px.bar(
                sum_data,
                x="Building",
                y="Total_Energy",
                color="Building",
                title="Total Energy Consumption (kWh)",
                labels={"Total_Energy": "kWh"}
            )
            st.plotly_chart(fig_bar_energy, use_container_width=True)
            
        with col_c2:
            fig_bar_cost = px.bar(
                sum_data,
                x="Building",
                y="Total_Cost",
                color="Building",
                title="Total Operational Cost (INR)",
                labels={"Total_Cost": "Cost (INR)"}
            )
            st.plotly_chart(fig_bar_cost, use_container_width=True)
            
        # Occupancy vs Energy
        fig_scatter_occ = px.scatter(
            df_filtered,
            x="Occupancy",
            y="Energy Consumption",
            color="Building",
            size="Running ACs",
            hover_data=["Hour", "Temperature"],
            title="Occupancy vs. Energy Draw (Bubble Size = Active ACs)",
            labels={"Energy Consumption": "kW"}
        )
        st.plotly_chart(fig_scatter_occ, use_container_width=True)

    with tab_correlation:
        st.subheader("Electrical & Environmental Correlation Matrix")
        st.write("Inspect how different variables impact campus load draws.")
        
        corr_matrix, cols = analytics_service.get_correlation_matrix()
        
        fig_heat = px.imshow(
            corr_matrix,
            x=cols,
            y=cols,
            color_continuous_scale="RdBu",
            zmin=-1, zmax=1,
            title="Pearson Correlation Coefficient Matrix"
        )
        fig_heat.update_layout(height=500)
        st.plotly_chart(fig_heat, use_container_width=True)

    with tab_weather:
        st.subheader("Weather impact on Campus Energy")
        
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            # Temperature vs Energy
            fig_temp = px.scatter(
                df_filtered,
                x="Temperature",
                y="Energy Consumption",
                color="Building",
                trendline="ols",
                title="Temperature (°C) vs. Energy Load (kW)",
                labels={"Energy Consumption": "kW"}
            )
            st.plotly_chart(fig_temp, use_container_width=True)
            
        with col_w2:
            # Humidity vs Energy
            fig_hum = px.scatter(
                df_filtered,
                x="Humidity",
                y="Energy Consumption",
                color="Building",
                trendline="ols",
                title="Humidity (%) vs. Energy Load (kW)",
                labels={"Energy Consumption": "kW"}
            )
            st.plotly_chart(fig_hum, use_container_width=True)
            
        # Boxplot by Weather Condition
        fig_box = px.box(
            df_filtered,
            x="Weather Condition",
            y="Energy Consumption",
            color="Building",
            title="Energy Load Distribution by Weather Condition",
            labels={"Energy Consumption": "kW"}
        )
        st.plotly_chart(fig_box, use_container_width=True)
