"""
Renders the KPI summary + LLM narrative into a PDF. Adapted from notebook
cells 9-10 (save_pdf / add_footer), refactored to take a dynamic output path
instead of a hardcoded "Executive_Report.pdf" and Colab's files.download().
"""
import re
 
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
 
 
def _add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.drawString(40, 20, "Business Intelligence Department")
    canvas.drawRightString(550, 20, f"Page {doc.page}")
    canvas.restoreState()
 
 
def _build_styles():
    styles = getSampleStyleSheet()
 
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=22, alignment=TA_CENTER, textColor=colors.black, spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading1"], fontName="Helvetica-Bold",
        fontSize=15, textColor=colors.black, spaceBefore=18, spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "BodyStyle", parent=styles["BodyText"], fontName="Helvetica",
        fontSize=11, leading=20, textColor=colors.black, spaceAfter=10, leftIndent=15,
    )
    return title_style, heading_style, body_style
 
 
def _narrative_to_flowables(narrative: str, heading_style, body_style):
    """
    The LLM returns markdown-ish text with section headings on their own
    line (e.g. 'Executive Summary'). Short standalone lines become headings,
    everything else becomes body text.
    """
    flowables = []
    for raw_line in narrative.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        is_heading = bool(re.match(r"^#{1,3}\s|^[A-Z][A-Za-z ]{2,40}$", line)) and len(line) < 45
        clean = re.sub(r"^#{1,3}\s*", "", line)
        flowables.append(Paragraph(clean, heading_style if is_heading else body_style))
    return flowables
 
 
def generate_pdf(
    output_path: str,
    narrative: str,
    total_revenue: float,
    completed_revenue: float,
    completion_rate: float,
    avg_order_value: float,
    average_rating: float,
) -> str:
    """Renders the report to output_path and returns that path."""
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40,
    )
 
    title_style, heading_style, body_style = _build_styles()
 
    story = [
        Paragraph("Executive Business Report", title_style),
        Spacer(1, 12),
        Paragraph(
            f"Total Revenue: ${total_revenue:,.2f} &nbsp;|&nbsp; "
            f"Completed: ${completed_revenue:,.2f} &nbsp;|&nbsp; "
            f"Completion Rate: {completion_rate:.2f}% &nbsp;|&nbsp; "
            f"AOV: ${avg_order_value:,.2f} &nbsp;|&nbsp; "
            f"Avg Rating: {average_rating:.2f}",
            body_style,
        ),
        Spacer(1, 20),
    ]
    story.extend(_narrative_to_flowables(narrative, heading_style, body_style))
 
    doc.build(story, onFirstPage=_add_footer, onLaterPages=_add_footer)
    return output_path
