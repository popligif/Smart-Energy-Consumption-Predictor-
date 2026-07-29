"""
Service layer for compiling formal executive PDF reports using ReportLab (FR-7).
"""
import os
import tempfile
from typing import Dict, Any, List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from services.dashboard_service import DashboardService
from services.recommendation_service import RecommendationService
from services.alert_service import AlertService
from services.ml_service import MLService

class ReportService:
    """Compiles clean, multi-page executive PDF documents with signature blocks and summaries."""
    
    def __init__(self) -> None:
        self.dashboard_service = DashboardService()
        self.recommender_service = RecommendationService()
        self.alert_service = AlertService()
        self.ml_service = MLService()

    def generate_pdf_report(self) -> str:
        """
        Compiles the full executive campus energy audit PDF.
        Returns the absolute filepath of the generated temporary PDF file.
        """
        kpis = self.dashboard_service.get_executive_kpis()
        health = self.dashboard_service.calculate_campus_health_score()
        brief = self.dashboard_service.generate_executive_brief()
        rankings = self.dashboard_service.get_building_rankings()
        alerts = self.alert_service.scan_for_alerts()
        recommendations = self.recommender_service.generate_recommendations()
        ml_metrics = self.ml_service.get_comparison_metrics()
        
        # Create temporary file
        temp_dir = tempfile.gettempdir()
        pdf_path = os.path.join(temp_dir, "miet_energy_executive_report.pdf")
        
        # Build Document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        styles = getSampleStyleSheet()
        
        # Custom color system
        navy = colors.HexColor("#1A365D")
        charcoal = colors.HexColor("#2D3748")
        teal = colors.HexColor("#319795")
        light_grey = colors.HexColor("#EDF2F7")
        alert_red = colors.HexColor("#E53E3E")
        
        # Custom styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=26,
            textColor=navy,
            spaceAfter=15,
            alignment=1  # Centered
        )
        
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=14,
            textColor=teal,
            spaceAfter=40,
            alignment=1
        )
        
        h1_style = ParagraphStyle(
            "SectionH1",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=navy,
            spaceBefore=15,
            spaceAfter=10,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            textColor=charcoal,
            leading=14,
            spaceAfter=10
        )
        
        table_text_style = ParagraphStyle(
            "TableText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=charcoal,
            leading=10
        )
        
        table_header_style = ParagraphStyle(
            "TableHeaderText",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=colors.white,
            leading=10
        )

        story = []
        
        # ------------------ PAGE 1: COVER PAGE ------------------
        story.append(Spacer(1, 100))
        story.append(Paragraph("MIET SMART CAMPUS", title_style))
        story.append(Paragraph("Energy Intelligence & Decision Support System", subtitle_style))
        
        story.append(Spacer(1, 40))
        
        # Metadata Table
        metadata_data = [
            [Paragraph("<b>Document Scope:</b>", body_style), Paragraph("Executive Energy Performance Report", body_style)],
            [Paragraph("<b>Target Institution:</b>", body_style), Paragraph("Meerut Institute of Engineering and Technology (MIET)", body_style)],
            [Paragraph("<b>Campus Health Rating:</b>", body_style), Paragraph(f"<b>{health['overall_score']}/100</b>", body_style)],
            [Paragraph("<b>Generated On:</b>", body_style), Paragraph("2026-07-29", body_style)],
        ]
        meta_table = Table(metadata_data, colWidths=[2.0*inch, 4.0*inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_grey),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E0")),
            ('PADDING', (0,0), (-1,-1), 12),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(meta_table)
        
        story.append(Spacer(1, 120))
        story.append(Paragraph("<font size=9 color='#A0AEC0'>Meerut Institute of Engineering and Technology - Energy Conservation Division</font>", title_style))
        story.append(PageBreak())
        
        # ------------------ PAGE 2: EXEC SUMMARY & KPIs ------------------
        story.append(Paragraph("Executive Summary", h1_style))
        story.append(Paragraph(brief, body_style))
        story.append(Spacer(1, 15))
        
        story.append(Paragraph("Campus Energy Performance KPIs", h1_style))
        # KPI Grid Table
        kpi_table_data = [
            [
                Paragraph("<b>Total Consumption</b><br/>" + f"{kpis['total_energy_kwh']:,.1f} kWh", body_style),
                Paragraph("<b>Utility Expenditure</b><br/>" + f"₹{kpis['total_cost_inr']:,.2f}", body_style)
            ],
            [
                Paragraph("<b>Carbon Footprint</b><br/>" + f"{kpis['total_carbon_kg']:,.1f} kg CO2", body_style),
                Paragraph("<b>Peak Demand load</b><br/>" + f"{kpis['peak_load_kw']:,.1f} kW ({kpis['peak_building']})", body_style)
            ]
        ]
        kpi_table = Table(kpi_table_data, colWidths=[3.25*inch, 3.25*inch])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 15),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 15))
        
        # Health Score breakdown
        story.append(Paragraph("Energy Score Card Breakdown", h1_style))
        score_data = [
            [Paragraph("Power Factor Compliance Score", body_style), Paragraph(f"{health['power_factor_score']}/100", body_style)],
            [Paragraph("HVAC Efficiency Score", body_style), Paragraph(f"{health['hvac_efficiency_score']}/100", body_style)],
            [Paragraph("Occupancy Waste Management Score", body_style), Paragraph(f"{health['occupancy_efficiency_score']}/100", body_style)],
            [Paragraph("Carbon Performance Index", body_style), Paragraph(f"{health['carbon_performance_score']}/100", body_style)]
        ]
        score_table = Table(score_data, colWidths=[4.0*inch, 2.5*inch])
        score_table.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(score_table)
        story.append(PageBreak())
        
        # ------------------ PAGE 3: BUILDING RANKINGS & ALERTS ------------------
        story.append(Paragraph("Building Performance Leaderboard", h1_style))
        rank_headers = ["Building Name", "Total kWh", "Cost (INR)", "Avg PF", "EEI (kWh/occ-hr)"]
        rank_rows = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in rank_headers]]
        for r in rankings:
            rank_rows.append([
                Paragraph(r["Building"], table_text_style),
                Paragraph(f"{r['Total Consumption (kWh)']:,.1f}", table_text_style),
                Paragraph(f"₹{r['Total Cost (INR)']:,.0f}", table_text_style),
                Paragraph(f"{r['Average Power Factor']:.3f}", table_text_style),
                Paragraph(f"{r['Energy Efficiency Index (kWh/occupant-hr)']:.3f}", table_text_style)
            ])
        rank_table = Table(rank_rows, colWidths=[2.0*inch, 1.1*inch, 1.1*inch, 1.0*inch, 1.3*inch])
        rank_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), navy),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_grey]),
            ('PADDING', (0,0), (-1,-1), 6),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        story.append(rank_table)
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Triggered Operational Smart Alerts", h1_style))
        if not alerts:
            story.append(Paragraph("No critical electrical or HVAC anomalies detected in this monitoring window.", body_style))
        else:
            alert_headers = ["Time", "Building", "Severity", "Category", "Telemetry Check"]
            alert_rows = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in alert_headers]]
            for a in alerts[:6]:  # Limit to top 6 to prevent overflow
                color_sev = alert_red if a["Severity"] == "Critical" else colors.HexColor("#DD6B20")
                alert_rows.append([
                    Paragraph(a["Timestamp"], table_text_style),
                    Paragraph(a["Building"], table_text_style),
                    Paragraph(f"<font color='{color_sev}'><b>{a['Severity']}</b></font>", table_text_style),
                    Paragraph(a["Category"], table_text_style),
                    Paragraph(a["Parameter"], table_text_style)
                ])
            alert_table = Table(alert_rows, colWidths=[1.1*inch, 1.6*inch, 0.8*inch, 1.3*inch, 1.7*inch])
            alert_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), charcoal),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_grey]),
                ('PADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            story.append(alert_table)
            if len(alerts) > 6:
                story.append(Spacer(1, 4))
                story.append(Paragraph(f"<font size=8 color='#E53E3E'>* Note: {len(alerts) - 6} additional alerts truncated from printing.</font>", body_style))
        story.append(PageBreak())
        
        # ------------------ PAGE 4: RECOMMENDATIONS & SIGN OFF ------------------
        story.append(Paragraph("AI Explainable Energy Mitigation Recommendations", h1_style))
        
        rec_headers = ["Recommendation Area", "Triggering Telemetry", "Annual savings", "Confidence"]
        rec_rows = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in rec_headers]]
        for r in recommendations:
            rec_rows.append([
                Paragraph(f"<b>{r['Title']}</b><br/>{r['Details']}", table_text_style),
                Paragraph(r["Trigger"], table_text_style),
                Paragraph(f"₹{r['Annual Savings (INR)']:,.0f}<br/>({r['Annual Carbon Offset (kg CO2)']:,.0f} kg CO2)", table_text_style),
                Paragraph(r["Confidence"], table_text_style)
            ])
        rec_table = Table(rec_rows, colWidths=[2.5*inch, 1.8*inch, 1.4*inch, 0.8*inch])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), navy),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_grey]),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(rec_table)
        story.append(Spacer(1, 40))
        
        # ML Scenario Section
        story.append(Paragraph("Scenario forecasting Model Quality Summary", h1_style))
        ml_txt = "The energy command centre scenario models are evaluated dynamically. Current performance scores: "
        for m_name, metrics in ml_metrics.items():
            ml_txt += f"<b>{m_name}</b> (R²: {metrics['R²']:.3f}, MAE: {metrics['MAE']:.2f} kW); "
        story.append(Paragraph(ml_txt, body_style))
        
        story.append(Spacer(1, 40))
        
        # Signature Block
        sig_data = [
            [
                Paragraph("<b>Prepared By:</b><br/><br/>___________________________<br/>Energy Auditor, Conservation Unit", body_style),
                Paragraph("<b>Approved By:</b><br/><br/>___________________________<br/>University Director, MIET", body_style)
            ]
        ]
        sig_table = Table(sig_data, colWidths=[3.25*inch, 3.25*inch])
        sig_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('PADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(sig_table)
        
        # Build PDF
        doc.build(story)
        return pdf_path
