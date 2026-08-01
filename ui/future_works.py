"""
Future Integrations Page — Displays proposed future R&D modules for the DSS.
"""
import streamlit as st

def render_future_works() -> None:

    # Academic Schedule vs Camera Verification Module
    st.markdown("""
    <div style="background:#FFFBEB;border-left:5px solid #F59E0B;border-radius:10px;padding:20px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,0.05);">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
            <div style="background:#F59E0B;color:white;width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.2rem;">
                📹
            </div>
            <div>
                <div style="font-size:1.1rem;font-weight:800;color:#92400E;">Academic Schedule vs. Real-Time Occupancy Verification</div>
                <div style="font-size:0.8rem;color:#B45309;font-weight:600;">Status: Proposed for Phase 2 Integration</div>
            </div>
        </div>
        
        <div style="font-size:0.9rem;color:#78350F;line-height:1.6;margin-bottom:14px;">
            <b>Problem Statement:</b> Resources are often wasted when a lecture is officially scheduled, but students execute a "mass bunk" or the class is unexpectedly cancelled. HVAC and lighting systems turn on automatically based on the timetable, consuming heavy power for an empty hall.
        </div>

        <div style="background:white;border-radius:8px;padding:16px;border:1px solid #FDE68A;">
            <div style="font-size:0.85rem;color:#92400E;font-weight:700;margin-bottom:8px;text-transform:uppercase;">
                Proposed AI Workflow
            </div>
            <ol style="font-size:0.85rem;color:#78350F;margin:0;padding-left:1.2rem;">
                <li style="margin-bottom:6px;"><b>Timetable Sync:</b> System reads the official university timetable for the day.</li>
                <li style="margin-bottom:6px;"><b>Pre-cooling Initiation:</b> HVAC starts 10 minutes prior to the scheduled lecture.</li>
                <li style="margin-bottom:6px;"><b>Camera Cross-Check:</b> At T+5 minutes into the lecture, AI processes the CCTV camera feed of the lecture hall.</li>
                <li style="margin-bottom:6px;"><b>Intelligent Override:</b> If occupancy is detected as 0 (or near zero, indicating a mass bunk), the system overrides the timetable and instantly shuts down HVAC and Lighting.</li>
                <li><b>Alert Dispatch:</b> An automated alert is sent to the Department Head and Energy Manager regarding the schedule mismatch.</li>
            </ol>
        </div>
        
        <div style="display:flex;gap:16px;margin-top:16px;">
            <span style="background:#FEF3C7;color:#92400E;padding:6px 14px;border-radius:20px;font-size:0.75rem;font-weight:700;">
                💡 Expected Saving: ~15-20% HVAC Waste
            </span>
            <span style="background:#FEF3C7;color:#92400E;padding:6px 14px;border-radius:20px;font-size:0.75rem;font-weight:700;">
                🛠️ Tech Stack: OpenCV + YOLOv8 + Smart Relays
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
