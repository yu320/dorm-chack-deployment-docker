import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime

from .. import schemas, models

import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import datetime

from .. import schemas, models

def generate_inspection_pdf(record: models.InspectionRecord) -> io.BytesIO:
    """
    Generates an inspection record as a PDF and returns it as a BytesIO buffer.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"Inspection Report #{record.id}", styles['h1']))
    elements.append(Spacer(1, 12))

    # Details Table
    details_data = [
        ["Student", record.student.full_name],
        ["Room", record.room.room_number],
        ["Status", record.status],
        ["Submitted At", record.created_at.strftime('%Y-%m-%d %H:%M')],
    ]
    details_table = Table(details_data)
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(details_table)
    elements.append(Spacer(1, 24))

    # Checklist Table
    elements.append(Paragraph("Checklist", styles['h2']))
    elements.append(Spacer(1, 12))
    checklist_data = [["Item", "Status", "Comment"]]
    for detail in record.details:
        checklist_data.append([detail.item.name, detail.status.value, detail.comment or ''])
    
    checklist_table = Table(checklist_data)
    checklist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
    ]))
    elements.append(checklist_table)
    elements.append(Spacer(1, 24))

    # Signature
    elements.append(Paragraph("Signature", styles['h2']))
    elements.append(Spacer(1, 12))
    if record.signature:
        try:
            img_data = base64.b64decode(record.signature.split(',')[1])
            img = Image(io.BytesIO(img_data), width=200, height=100)
            elements.append(img)
        except (IndexError, base64.binascii.Error):
            elements.append(Paragraph("Invalid signature data.", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return buffer
