"""
UI component for displaying explainable AI recommendations and ROI analysis (FR-5).
"""
import streamlit as st
from services.recommendation_service import RecommendationService

def render_recommendations() -> None:
    """Renders the AI Recommendations tab in Streamlit."""
    st.header("💡 AI Energy Recommendation Engine")
    st.write(
        "Dynamic, data-driven operational improvements compiled by scanning campus metrics."
    )
    
    recommender = RecommendationService()
    recs = recommender.generate_recommendations()
    
    # Calculate overall potentials
    tot_savings_inr = sum(r["Annual Savings (INR)"] for r in recs)
    tot_offset_co2 = sum(r["Annual Carbon Offset (kg CO2)"] for r in recs)
    
    # Financial Banner with layout styling
    st.markdown(
        f"""
        <div style="background-color: #E6FFFA; border: 1px solid #319795; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
            <h3 style="color: #234E52; margin-top: 0; margin-bottom: 8px;">Total Campus Savings Potential</h3>
            <div style="display: flex; gap: 30px;">
                <div>
                    <span style="font-size: 0.85rem; color: #2C7A7B; font-weight: 600; text-transform: uppercase;">Annual Cost Reduction</span><br/>
                    <span style="font-size: 1.8rem; font-weight: 800; color: #285E61;">₹{tot_savings_inr:,.2f} / year</span>
                </div>
                <div>
                    <span style="font-size: 0.85rem; color: #2C7A7B; font-weight: 600; text-transform: uppercase;">Annual Carbon Mitigation</span><br/>
                    <span style="font-size: 1.8rem; font-weight: 800; color: #285E61;">{tot_offset_co2:,.1f} kg CO₂ / year</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.write(f"Showing {len(recs)} customized optimization recommendations:")
    
    for r in recs:
        # Determine confidence color
        conf = r["Confidence"]
        conf_color = "#38A169" if conf == "High" else ("#DD6B20" if conf == "Medium" else "#E53E3E")
        
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px; margin-bottom: 15px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                    <div>
                        <span style="font-size: 0.8rem; color: #718096; text-transform: uppercase; font-weight: bold; letter-spacing: 0.5px;">
                            {r['Category']}
                        </span>
                        <h4 style="margin: 3px 0 0 0; color: #2D3748; font-size: 1.15rem; font-weight: 700;">
                            {r['Title']}
                        </h4>
                    </div>
                    <span style="background-color: {conf_color}1A; color: {conf_color}; font-size: 0.75rem; font-weight: bold; padding: 4px 10px; border-radius: 12px; border: 1px solid {conf_color};">
                        {conf} Confidence
                    </span>
                </div>
                
                <div style="font-size: 0.95rem; color: #4A5568; margin-bottom: 12px; line-height: 1.5;">
                    <b>Proposed Action:</b> {r['Details']}
                </div>
                
                <div style="background-color: #F7FAFC; padding: 12px; border-radius: 6px; font-size: 0.85rem; color: #4A5568; margin-bottom: 12px; border-left: 3px solid #CBD5E0;">
                    <b>Triggering Telemetry:</b> <i>{r['Trigger']}</i>
                </div>
                
                <div style="display: flex; gap: 20px; font-size: 0.85rem; font-weight: bold; margin-bottom: 12px;">
                    <span style="color: #2F855A;">💰 Est. Annual Savings: ₹{r['Annual Savings (INR)']:,.2f}</span>
                    <span style="color: #319795;">🌱 Carbon Offset: {r['Annual Carbon Offset (kg CO2)']:,.1f} kg CO₂</span>
                </div>
                
                <div style="font-size: 0.85rem; color: #718096; line-height: 1.4; border-top: 1px solid #EDF2F7; padding-top: 10px;">
                    <b>Explainable AI Reasoning:</b> {r['Reasoning']}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
