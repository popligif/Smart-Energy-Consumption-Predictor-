"""
UI component for generating and downloading the professional executive energy audit PDF report (FR-7).
"""
import streamlit as st
import os
from services.report_service import ReportService

def render_reports() -> None:
    """Renders the PDF Report generation UI in Streamlit."""
    
    st.markdown(
        """
        <div style="background-color: #F7FAFC; border: 1px solid #E2E8F0; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
            <h4 style="color: #2D3748; margin-top: 0; margin-bottom: 10px;">PDF Report Contents</h4>
            <ul style="color: #4A5568; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">
                <li><b>Cover Page:</b> Institution credentials, campus health ratings, and metadata blocks.</li>
                <li><b>Executive Summary:</b> Concise operational brief outlining energy, cost, and carbon performance.</li>
                <li><b>Campus KPIs Grid:</b> Tabulated totals for kWh consumption, budget expenditures, and peak loads.</li>
                <li><b>Building Efficiency Leaderboard:</b> Rankings sorted by consumption and Energy Efficiency Index (EEI).</li>
                <li><b>Smart Alerts Ledger:</b> Log of triggered electrical, idle load, and HVAC waste anomalies.</li>
                <li><b>AI Recommendations:</b> List of cost-reduction items detailing trigger telemetry, ROI, and carbon offsets.</li>
                <li><b>Model Performance Summary:</b> Regression quality metrics (R², MAE, RMSE) for planning.</li>
                <li><b>Director Sign-Off Block:</b> formal lines for operational approval.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    report_service = ReportService()
    
    # Trigger PDF Generation
    if st.button("🚀 Compile Executive Energy Audit Report", type="primary"):
        with st.spinner("Generating document layouts, compiling tables, and drawing PDF vector story..."):
            try:
                pdf_path = report_service.generate_pdf_report()
                
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_data = f.read()
                        
                    st.success("✅ Executive energy audit PDF compiled successfully!")
                    
                    st.download_button(
                        label="📥 Download Executive PDF Report",
                        data=pdf_data,
                        file_name="miet_campus_energy_audit_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("Failed to generate PDF. Output file path was not created.")
            except Exception as e:
                st.error(f"Failed to compile PDF report: {e}")
                st.exception(e)
