"""
Smart Alerts Page — Completely rewritten with meaningful, decision-oriented alerts.
Covers: Hybrid energy switching decisions, load sharing recommendations,
        threshold scientific basis, and operational severity classification.
"""
import streamlit as st
import pandas as pd
from services.alert_service import AlertService
from services.data_service import DataService

# ── Threshold scientific basis ────────────────────────────────────────────────
THRESHOLD_RATIONALE = {
    "Power Factor < 0.90": {
        "basis": "IEEE 519-2014 & BEE (Bureau of Energy Efficiency) India guidelines",
        "significance": (
            "Power Factor (PF) quantifies how efficiently electrical power is converted into useful work. "
            "A PF below 0.90 means reactive current is wasting up to 10-19% of transmission capacity. "
            "DISCOM utilities impose a reactive energy surcharge (₹/kVArh) when PF < 0.95, and power "
            "transformers must carry excess current — increasing copper and iron losses by up to 21%."
        ),
        "hybrid_action": (
            "Switch to battery-backed inverter mode to supply reactive power locally. "
            "Battery inverters can inject reactive current at PF = 1.0, eliminating reactive import from grid."
        )
    },
    "HVAC Inefficiency": {
        "basis": "ASHRAE 90.1-2019: Minimum Energy Performance Standards for Buildings",
        "significance": (
            "HVAC typically accounts for 40-60% of a building's energy consumption. "
            "Running ACs below 24°C outdoor setpoint violates the economiser mandate — "
            "free cooling via outdoor air or mixed-mode ventilation should be used instead. "
            "Every 1°C thermostat setback saves approximately 3-5% HVAC energy (ISHRAE standard)."
        ),
        "hybrid_action": (
            "Activate economiser mode; use solar power for residual HVAC load during daytime. "
            "Load shift HVAC pre-cooling to solar peak hours (10 AM – 3 PM) to zero grid import."
        )
    },
    "Idle Load / Empty Room Waste": {
        "basis": "IEA (International Energy Agency) — Zero Energy Building (ZEB) Protocol",
        "significance": (
            "Phantom / standby loads in unoccupied rooms represent 5-15% of total campus energy "
            "with zero productive output. This includes computers in sleep-but-powered mode (~50W each), "
            "ballast lighting (~20W/tube), and fan motors running on timer circuits after occupants leave."
        ),
        "hybrid_action": (
            "Activate IoT occupancy-linked relay circuit. "
            "Idle loads can be cut entirely via smart MCBs, reducing wasted kWh with no operational impact. "
            "Battery covers standby server and security systems during idle periods."
        )
    },
    "Peak Load Surge > 1.5x Median": {
        "basis": "CEA (Central Electricity Authority) Demand Side Management Regulations 2022",
        "significance": (
            "Peak demand sets the Demand Charge (₹/kW/month) billed by the utility — "
            "the single largest controllable cost for large consumers. A spike 1.5x above the "
            "median baseline indicates simultaneous coincident loads (labs + ACs + computers all ON together). "
            "Reducing the 15-minute peak average by 10 kW saves ₹15,000-25,000/month at standard DISCOm tariffs."
        ),
        "hybrid_action": (
            "Engage battery discharge at peak. Battery can supply 30 kW for 4 hours. "
            "Load sharing: Route 30% of Workshop Building load to Block D feeder during surge hours. "
            "Alert energy manager to manually shed non-critical AC units in vacant floors."
        )
    },
    "Vacant Room — Camera Feed Detection (Occupancy ≤ 2)": {
        "basis": "IEA ZEB Protocol & ECBC 2017 (Energy Conservation Building Code India) — Occupancy-Based Load Control",
        "significance": (
            "Smart camera or PIR sensor feed detects near-vacant rooms (≤ 2 persons) where ACs, fans, or "
            "lighting circuits remain energised. This phantom load wastes 0.5–3 kW per room per hour. "
            "Across 6 buildings × 3 floors, even 10% of rooms left unattended during off-hours can add "
            "15–45 kWh/day of avoidable consumption — equivalent to ₹120–360/day at current tariffs."
        ),
        "hybrid_action": (
            "Deploy IoT occupancy-linked relay control via smart MCBs. Until automation is installed, "
            "the system generates real-time Guard Dispatch Alerts — security personnel are notified with "
            "building, floor, and device details to manually shut down loads within 15 minutes. "
            "Battery backup covers only essential security and server loads during guard response window."
        )
    }
}

def render_alerts() -> None:
    alert_svc = AlertService()
    data_svc  = DataService()
    df = data_svc.load_dataset()

    alerts = alert_svc.scan_for_alerts()
    settings = data_svc.settings_manager.load_settings()

    # ── Section Header ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="padding:20px 0 4px 0;">
      <div style="font-size:1.5rem;font-weight:800;color:#0F172A;">🔔 Smart Operational Alerts</div>
      <div style="color:#94A3B8;font-size:0.82rem;">
        Decision-oriented alerts for hybrid energy management and campus load sharing
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Summary Metric Row ─────────────────────────────────────────────────────
    crit_alerts = [a for a in alerts if a["Severity"] == "Critical"]
    warn_alerts = [a for a in alerts if a["Severity"] == "Warning"]

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:3px solid #EF4444;">
          <div style="font-size:0.75rem;color:#94A3B8;font-weight:600;text-transform:uppercase;">
            Total Active Alerts
          </div>
          <div style="font-size:2.2rem;font-weight:800;color:#0F172A;">{len(alerts)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:3px solid #EF4444;">
          <div style="font-size:0.75rem;color:#94A3B8;font-weight:600;text-transform:uppercase;">
            Critical Alerts
          </div>
          <div style="font-size:2.2rem;font-weight:800;color:#EF4444;">{len(crit_alerts)}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top:3px solid #F59E0B;">
          <div style="font-size:0.75rem;color:#94A3B8;font-weight:600;text-transform:uppercase;">
            Warning Alerts
          </div>
          <div style="font-size:2.2rem;font-weight:800;color:#F59E0B;">{len(warn_alerts)}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        # Estimate daily cost impact
        tariff = settings.get("electricity_tariff")
        waste_kw = sum(
            float(a["Parameter"].split("Energy: ")[-1].split(" kW")[0])
            for a in crit_alerts if "Energy:" in a["Parameter"]
        ) if crit_alerts else 0
        daily_waste_cost = round(waste_kw * tariff, 0)
        st.markdown(f"""
        <div class="kpi-card" style="border-top:3px solid #10B981;">
          <div style="font-size:0.75rem;color:#94A3B8;font-weight:600;text-transform:uppercase;">
            Est. Daily Cost at Risk
          </div>
          <div style="font-size:2.2rem;font-weight:800;color:#10B981;">₹{daily_waste_cost:,.0f}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Threshold Scientific Basis (Expandable) ────────────────────────────────
    with st.expander("📐 Threshold Basis & Scientific Rationale — Why these thresholds?", expanded=False):
        for thresh_name, details in THRESHOLD_RATIONALE.items():
            st.markdown(f"""
            <div style="background:#F8FAFC;border-radius:10px;padding:16px;margin-bottom:14px;
                        border-left:4px solid #059669;">
              <div style="font-size:0.95rem;font-weight:700;color:#0F172A;margin-bottom:6px;">
                🎯 {thresh_name}
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div>
                  <div style="font-size:0.72rem;color:#059669;font-weight:700;
                               text-transform:uppercase;margin-bottom:4px;">
                    Standard / Basis
                  </div>
                  <div style="font-size:0.8rem;color:#475569;line-height:1.5;">
                    {details['basis']}
                  </div>
                </div>
                <div>
                  <div style="font-size:0.72rem;color:#10B981;font-weight:700;
                               text-transform:uppercase;margin-bottom:4px;">
                    Engineering Significance
                  </div>
                  <div style="font-size:0.8rem;color:#475569;line-height:1.5;">
                    {details['significance']}
                  </div>
                </div>
              </div>
              <div style="margin-top:10px;background:#ECFDF5;border-radius:6px;padding:10px;">
                <div style="font-size:0.72rem;color:#047857;font-weight:700;
                             text-transform:uppercase;margin-bottom:3px;">
                  ⚡ Hybrid Energy / Load Sharing Action
                </div>
                <div style="font-size:0.8rem;color:#064E3B;line-height:1.5;">
                  {details['hybrid_action']}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Filters ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-size:1.0rem;font-weight:700;color:#0F172A;margin-bottom:8px;">
      Filter Active Alerts
    </div>""", unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns(3, gap="medium")
    with col_f1:
        sev_filter  = st.selectbox("Severity", ["All","Critical","Warning"], key="alert_sev")
    with col_f2:
        bldg_opts   = ["All"] + sorted(set(a["Building"] for a in alerts))
        bldg_filter = st.selectbox("Building",  bldg_opts, key="alert_bldg")
    with col_f3:
        cat_opts    = ["All"] + sorted(set(a["Category"] for a in alerts))
        cat_filter  = st.selectbox("Category", cat_opts, key="alert_cat")

    filtered = alerts
    if sev_filter  != "All": filtered = [a for a in filtered if a["Severity"] == sev_filter]
    if bldg_filter != "All": filtered = [a for a in filtered if a["Building"] == bldg_filter]
    if cat_filter  != "All": filtered = [a for a in filtered if a["Category"] == cat_filter]

    if not filtered:
        st.success("✅ No alerts match the selected filters. Campus operating within safe bounds.")
        return

    st.markdown(f"""
    <div style="font-size:0.82rem;color:#64748B;margin:8px 0 16px 0;">
      Showing <b>{len(filtered)}</b> active alert(s)
    </div>""", unsafe_allow_html=True)
    
    MAX_ALERTS_RENDER = 15
    if len(filtered) > MAX_ALERTS_RENDER:
        st.info(f"⚡ To ensure optimal performance, only the latest {MAX_ALERTS_RENDER} alerts are displayed. Use filters to narrow down.")
        display_alerts = filtered[:MAX_ALERTS_RENDER]
    else:
        display_alerts = filtered

    # ── Alert Cards ────────────────────────────────────────────────────────────
    for alert in display_alerts:
        sev    = alert["Severity"]
        cat    = alert["Category"]
        bldg   = alert["Building"]
        hour   = alert["Hour"]
        msg    = alert["Message"]
        param  = alert["Parameter"]
        thresh = alert["Threshold"]
        ts     = alert["Timestamp"]

        sev_color = "#EF4444" if sev == "Critical" else "#F59E0B"
        bg_color  = "#FFF5F5" if sev == "Critical" else "#FFFBEB"

        # ── Decision support block based on category ───────────────────────────
        if cat == "Electrical":
            decision = (
                "🔌 <b>Load Sharing Decision:</b> Install APFC capacitor bank at building feeder. "
                "Alternatively, switch inverter-battery to reactive power compensation mode (Q-control). "
                "Prioritise this building for capacitor bank in next maintenance cycle."
            )
            hybrid_action = (
                "⚡ <b>Hybrid Action:</b> Battery inverter can supply reactive power locally at zero cost. "
                "Enable Q-mode on the building's UPS/inverter to correct PF to ≥0.95 immediately."
            )
        elif cat == "HVAC Inefficiency":
            decision = (
                "❄️ <b>Load Sharing Decision:</b> If adjoining building has unused cooling capacity, "
                "redistribute occupants temporarily. Schedule a thermostat setback of +2°C on all AC units in this block."
            )
            hybrid_action = (
                "☀️ <b>Hybrid Action:</b> Pre-cool building using solar power during 10 AM–2 PM window. "
                "Disconnect grid HVAC during solar peak; battery tops up during cloud cover. "
                "This alone reduces grid HVAC import by up to 60% on clear days."
            )
        elif cat == "Idle Waste":
            decision = (
                "🏢 <b>Load Sharing Decision:</b> No active occupants to shift. "
                "Issue immediate shutdown directive to building operations staff. "
                "Enable smart relay circuit to cut all non-essential loads automatically."
            )
            hybrid_action = (
                "🔋 <b>Hybrid Action:</b> Switch idle floor circuits to battery supply only. "
                "This isolates the wasted load from grid import, reducing billed units without physical shutdown."
            )
        else:
            decision = (
                "📊 <b>Load Sharing Decision:</b> Identify which departments are running coincident loads. "
                "Stagger laboratory sessions by 30 minutes to flatten the demand curve and avoid peak billing."
            )
            hybrid_action = (
                "⚡ <b>Hybrid Action:</b> Activate battery discharge during the surge window. "
                f"Battery can supply 30 kW for 4 hours — enough to shave the peak at Hour {hour} entirely."
            )

        # Check for Guard Alert category
        guard_action = alert.get("Guard_Action", "")
        is_guard_alert = cat == "Vacant Room — Guard Alert"

        # Compute potential savings
        pf_val = df[df["Building"]==bldg]["Power Factor"].mean()
        energy_val = df[df["Building"]==bldg]["Energy Consumption"].mean()
        tariff_rate = settings.get("electricity_tariff")
        carbon_factor = settings.get("carbon_factor")
        est_daily_savings = round(energy_val * 0.1 * tariff_rate, 2)
        est_carbon_saved  = round(energy_val * 0.1 * carbon_factor, 2)

        st.markdown(f"""
        <div style="background:{bg_color};border:1px solid {sev_color}33;border-left:5px solid {sev_color};
                    border-radius:10px;padding:18px;margin-bottom:16px;">

          <!-- Header Row -->
          <div style="display:flex;justify-content:space-between;
                      align-items:flex-start;margin-bottom:10px;">
            <div>
              <span style="background:{sev_color};color:white;font-size:0.7rem;font-weight:700;
                           padding:2px 10px;border-radius:20px;text-transform:uppercase;">
                {sev}
              </span>
              <span style="background:#F1F5F9;color:#475569;font-size:0.7rem;font-weight:600;
                           padding:2px 10px;border-radius:20px;margin-left:6px;">
                {cat}
              </span>
            </div>
            <span style="font-size:0.72rem;color:#94A3B8;">🕒 {ts}</span>
          </div>

          <!-- Main Message -->
          <div style="font-size:0.92rem;font-weight:600;color:#0F172A;margin-bottom:6px;">
            {msg}
          </div>

          <!-- Telemetry Row -->
          <div style="display:flex;gap:16px;font-size:0.78rem;color:#64748B;margin-bottom:12px;">
            <span>📍 <b>{bldg}</b></span>
            <span>⏰ Hour: <b>{hour}:00</b></span>
            <span>📊 Reading: <b>{param}</b></span>
            <span>🎯 Threshold: <b>{thresh}</b></span>
          </div>

          <!-- Decision + Hybrid Grid -->
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
            <div style="background:white;border-radius:8px;padding:12px;
                        border:1px solid #E2E8F0;">
              <div style="font-size:0.7rem;color:#475569;font-weight:700;
                           text-transform:uppercase;margin-bottom:4px;">
                Management Decision
              </div>
              <div style="font-size:0.8rem;color:#374151;line-height:1.5;">
                {decision}
              </div>
            </div>
            <div style="background:#ECFDF5;border-radius:8px;padding:12px;
                        border:1px solid #D1FAE5;">
              <div style="font-size:0.7rem;color:#047857;font-weight:700;
                           text-transform:uppercase;margin-bottom:4px;">
                Hybrid Energy Action
              </div>
              <div style="font-size:0.8rem;color:#064E3B;line-height:1.5;">
                {hybrid_action}
              </div>
            </div>
          </div>
        """, unsafe_allow_html=True)

        # Render Guard Dispatch card if applicable
        if is_guard_alert and guard_action:
            floor_val = alert.get("Floor", "?")
            st.markdown(f"""
          <div style="background:#FFF7ED;border:2px solid #F97316;border-radius:10px;
                      padding:16px;margin:-8px 0 12px 0;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
              <div style="background:#F97316;color:white;width:36px;height:36px;border-radius:10px;
                          display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🛡️</div>
              <div>
                <div style="font-size:0.88rem;font-weight:700;color:#9A3412;">Guard Dispatch Order</div>
                <div style="font-size:0.72rem;color:#C2410C;">Auto-generated from camera feed · Floor {floor_val}, {bldg}</div>
              </div>
            </div>
            <div style="font-size:0.82rem;color:#7C2D12;line-height:1.6;">
              {guard_action}
            </div>
            <div style="display:flex;gap:12px;margin-top:12px;font-size:0.75rem;">
              <span style="background:#FDBA74;color:#7C2D12;padding:3px 12px;
                           border-radius:16px;font-weight:700;">⏱ Response: 15 min</span>
              <span style="background:#FED7AA;color:#9A3412;padding:3px 12px;
                           border-radius:16px;font-weight:600;">📍 Floor {floor_val} · {bldg}</span>
              <span style="background:#FFEDD5;color:#C2410C;padding:3px 12px;
                           border-radius:16px;font-weight:600;">📷 Camera Verified</span>
            </div>
          </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
          <!-- Financial Impact -->
          <div style="display:flex;gap:20px;font-size:0.78rem;background:white;
                      border-radius:8px;padding:10px 14px;border:1px solid #E2E8F0;">
            <span>💰 Est. Daily Saving if resolved:
              <b style="color:#059669;">₹{est_daily_savings:,.2f}</b>
            </span>
            <span>🌱 Carbon Offset:
              <b style="color:#059669;">{est_carbon_saved:.2f} kg CO₂/day</b>
            </span>
            <span>📉 Energy Reduction Potential:
              <b style="color:#059669;">~10%</b>
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

