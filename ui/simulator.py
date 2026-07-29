"""
UI component for the Scenario Planning Simulator, What-If simulation, and ML model comparison (FR-4).
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from services.ml_service import MLService
from services.data_service import DataService

def render_simulator() -> None:
    """Renders the Scenario Simulator tab with sliders, prediction metrics, and model comparisons."""
    st.header("🔮 Scenario Planning Simulator")
    st.write("Run what-if scenario analyses to evaluate how operational adjustments affect campus power draws and budgets.")
    
    # Initialize ML service
    ml_service = MLService()
    data_service = DataService()
    df = data_service.load_dataset()
    
    # Check best model
    best_model = ml_service.best_model_name
    metrics = ml_service.get_comparison_metrics()
    
    # Create simulator panel and outputs
    col_sim_left, col_sim_right = st.columns([1, 1])
    
    with col_sim_left:
        st.subheader("Simulate Operational Parameters")
        
        building = st.selectbox("Select Target Building", options=sorted(df["Building"].unique().tolist()))
        hour = st.slider("Hour of the Day", min_value=0, max_value=23, value=12)
        
        # Environmental sliders
        temp = st.slider("Outdoor Temperature (°C)", min_value=15.0, max_value=45.0, value=30.0)
        humidity = st.slider("Outdoor Humidity (%)", min_value=20.0, max_value=100.0, value=60.0)
        
        # Occupancy & loads sliders
        occupancy = st.slider("Floor Occupancy (Persons)", min_value=0, max_value=200, value=50)
        running_acs = st.slider("Active Air Conditioner Units", min_value=0, max_value=20, value=5)
        running_computers = st.slider("Active Computers", min_value=0, max_value=200, value=40)
        
        # Load calibration inputs
        lighting_load = st.slider("Lighting Load Capacity (kW)", min_value=0.0, max_value=10.0, value=2.0)
        hvac_load = st.slider("HVAC Load Capacity (kW)", min_value=0.0, max_value=30.0, value=7.5)

    with col_sim_right:
        st.subheader("Simulation Results")
        
        # Run prediction
        res = ml_service.predict_scenario(
            building=building,
            hour=hour,
            temp=temp,
            humidity=humidity,
            occupancy=occupancy,
            running_acs=running_acs,
            running_computers=running_computers,
            lighting_load=lighting_load,
            hvac_load=hvac_load
        )
        
        # KPI widgets
        c1, c2, c3 = st.columns(3)
        
        delta_val = f"{res['difference_kw']:+.2f} kW ({res['percentage_change']:+.1f}%)"
        
        c1.metric(
            label="Predicted Energy", 
            value=f"{res['predicted_energy_kw']:.2f} kW", 
            delta=delta_val,
            delta_color="inverse"
        )
        c2.metric(
            label="Estimated Cost / Hr", 
            value=f"₹{res['predicted_cost_inr']:.2f}",
            help="Based on current electricity rates."
        )
        c3.metric(
            label="Carbon footprint / Hr", 
            value=f"{res['predicted_carbon_kg']:.2f} kg",
            help="Based on grid carbon coefficients."
        )
        
        # AI Explanation
        st.markdown(
            f"""
            <div style="background-color: #F0FFF4; border-left: 5px solid #38A169; padding: 15px; border-radius: 6px; margin: 15px 0;">
                <h4 style="color: #276749; margin-top: 0; margin-bottom: 5px;">Explainable AI Analysis</h4>
                <p style="color: #2F855A; font-size: 0.95rem; line-height: 1.5; margin: 0;">{res['explanation']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Feature Importance Plot
        st.subheader("Model Feature Importance")
        st.write("Identifies parameters most influential in predicting energy loads.")
        
        if ml_service.feature_importances:
            # Aggregate building-level importances to keep visualization clean
            raw_imp = ml_service.feature_importances
            agg_imp = {}
            for k, v in raw_imp.items():
                if "Building_" in k:
                    agg_imp["Building ID (Location)"] = agg_imp.get("Building ID (Location)", 0.0) + v
                else:
                    agg_imp[k] = v
                    
            df_imp = pd.DataFrame(list(agg_imp.items()), columns=["Feature", "Importance"]).sort_values(by="Importance", ascending=True)
            
            fig_imp = px.bar(
                df_imp,
                y="Feature",
                x="Importance",
                orientation="h",
                color="Importance",
                color_continuous_scale="Agsunset",
                height=250
            )
            fig_imp.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig_imp, use_container_width=True)
            
    st.markdown("---")
    
    # 3. Model Training & Validation details
    st.subheader("ML Models Performance Evaluation & Selection")
    st.write(
        f"Four model structures are evaluated in the background. The system automatically selected "
        f"**{best_model}** as the most accurate regressor for scenario predictions."
    )
    
    # Convert metrics dict to DF for table formatting
    metrics_df = pd.DataFrame(metrics).T.reset_index().rename(columns={"index": "Model Name"})
    
    # Highlight best model
    def highlight_best(row):
        if row["Model Name"] == best_model:
            return ["background-color: #E6FFFA; font-weight: bold; color: #00A389"] * len(row)
        return [""] * len(row)
        
    st.dataframe(
        metrics_df.style.apply(highlight_best, axis=1),
        use_container_width=True,
        hide_index=True
    )
    
    # Technical limits note
    st.info(
        "🧠 **Model Methodology & Dataset Awareness Notice:** Models were trained on the exact 144 records "
        "covering 6 buildings over a 24-hour period. Therefore, this model performs spatial interpolation and parameter "
        "what-if analysis; it does not forecast time-series trends into future weeks due to temporal limitations of the input dataset."
    )
