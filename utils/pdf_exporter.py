import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from core.exceptions import ValidationError


class PDFExporter:
    """Utility class to generate clean, structured PDF documents for FurFind reports."""

    COLOR_PRIMARY = colors.HexColor("#18181B")      # Charcoal / Dark accent
    COLOR_TEXT = colors.HexColor("#111827")         # Main dark text
    COLOR_MUTED = colors.HexColor("#71717A")        # Muted text
    COLOR_BORDER = colors.HexColor("#E4E4E7")       # Border grey
    COLOR_BG_LIGHT = colors.HexColor("#F4F4F5")     # Light background fill

    @staticmethod
    def _create_header(title_text: str, subtitle_text: str) -> list:
        """Helper to build a unified header for PDF exports."""
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'HeaderTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=PDFExporter.COLOR_PRIMARY
        )
        
        subtitle_style = ParagraphStyle(
            'HeaderSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=PDFExporter.COLOR_MUTED
        )

        elements = [
            Paragraph("<b>FurFind</b> — Pet Search & Recovery System", title_style),
            Spacer(1, 4),
            Paragraph(subtitle_text, subtitle_style),
            Spacer(1, 4),
            Paragraph(f"<b>Generated On:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", subtitle_style),
            Spacer(1, 10),
            HRFlowable(width="100%", thickness=1, color=PDFExporter.COLOR_BORDER, spaceAfter=15)
        ]
        return elements

    @classmethod
    def export_pet_report(cls, report, output_path: str) -> str:
        """
        Exports an individual Pet Report (Lost or Found) as a structured PDF summary.
        
        :param report: PetReport object containing report details
        :param output_path: Destination path for the generated PDF
        :return: Path to the generated PDF
        """
        if not output_path.lower().endswith('.pdf'):
            output_path += '.pdf'

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        story = cls._create_header("Pet Details Report", f"Official Summary Sheet — Report #{report.report_id}")
        styles = getSampleStyleSheet()

        label_style = ParagraphStyle('LabelStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=cls.COLOR_PRIMARY)
        value_style = ParagraphStyle('ValueStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=cls.COLOR_TEXT)

        # Build Form Details Grid
        details_data = [
            [Paragraph("Report Category:", label_style), Paragraph(str(report.category), value_style),
             Paragraph("Status:", label_style), Paragraph(str(report.status), value_style)],
            [Paragraph("Pet Name:", label_style), Paragraph(str(report.pet_name), value_style),
             Paragraph("Species:", label_style), Paragraph(str(report.species), value_style)],
            [Paragraph("Breed:", label_style), Paragraph(str(report.breed), value_style),
             Paragraph("Gender:", label_style), Paragraph(str(report.gender), value_style)],
            [Paragraph("Primary Color:", label_style), Paragraph(str(report.primary_color), value_style),
             Paragraph("Secondary Color:", label_style), Paragraph(str(report.secondary_color or "N/A"), value_style)],
            [Paragraph("Incident Date:", label_style), Paragraph(str(report.incident_date), value_style),
             Paragraph("Location:", label_style), Paragraph(str(report.location), value_style)],
            [Paragraph("Distinguishing Marks:", label_style), Paragraph(str(report.distinguishing_marks or "None"), value_style), "", ""]
        ]

        details_table = Table(details_data, colWidths=[1.4*inch, 2.2*inch, 1.4*inch, 2.2*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cls.COLOR_BG_LIGHT),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, cls.COLOR_BORDER),
            ('BOX', (0, 0), (-1, -1), 1, cls.COLOR_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('SPAN', (1, 5), (3, 5)), # Merge distinguishing marks across remaining columns
        ]))

        story.append(details_table)
        story.append(Spacer(1, 15))

        # Attached Photo Section
        if hasattr(report, 'photo_path') and report.photo_path and os.path.exists(report.photo_path):
            try:
                story.append(Paragraph("<b>Attached Photo Preview:</b>", label_style))
                story.append(Spacer(1, 8))
                img = Image(report.photo_path, width=3.5*inch, height=2.6*inch)
                story.append(img)
            except Exception:
                story.append(Paragraph("<i>[Image preview unavailable]</i>", value_style))

        doc.build(story)
        return output_path

    @classmethod
    def export_audit_logs(cls, logs: list, output_path: str) -> str:
        """
        Exports system audit logs into a formatted tabular PDF document.
        
        :param logs: List of AuditLog object instances or dictionaries
        :param output_path: Output file destination path
        :return: Destination path to generated PDF file
        """
        if not output_path.lower().endswith('.pdf'):
            output_path += '.pdf'

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        story = cls._create_header("System Audit Trail", "System Activity History & Audit Log Export")
        styles = getSampleStyleSheet()

        header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, textColor=colors.white)
        cell_style = ParagraphStyle('CellStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=8, textColor=cls.COLOR_TEXT)

        # Table Header Row
        table_data = [[
            Paragraph("Log ID", header_style),
            Paragraph("Timestamp", header_style),
            Paragraph("User ID", header_style),
            Paragraph("Action", header_style),
            Paragraph("Details", header_style)
        ]]

        for log in logs:
            log_id = str(getattr(log, 'log_id', log.get('log_id', 'N/A')))
            timestamp = str(getattr(log, 'timestamp', log.get('timestamp', 'N/A')))
            user_id = str(getattr(log, 'user_id', log.get('user_id', 'N/A')))
            action = str(getattr(log, 'action', log.get('action', 'N/A')))
            details = str(getattr(log, 'details', log.get('details', 'N/A')))

            table_data.append([
                Paragraph(log_id, cell_style),
                Paragraph(timestamp, cell_style),
                Paragraph(user_id, cell_style),
                Paragraph(action, cell_style),
                Paragraph(details, cell_style)
            ])

        logs_table = Table(table_data, colWidths=[0.7*inch, 1.4*inch, 0.8*inch, 1.6*inch, 2.7*inch])
        logs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), cls.COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, cls.COLOR_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, cls.COLOR_BG_LIGHT])
        ]))

        story.append(logs_table)
        doc.build(story)
        return output_path