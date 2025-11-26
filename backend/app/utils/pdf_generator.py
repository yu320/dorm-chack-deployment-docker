from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os
import base64
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

STATUS_TRANSLATIONS = {
    "submitted": "已提交",
    "pending": "待處理",
    "approved": "已核准",
    "rejected": "已拒絕",
    "ok": "正常",
    "damaged": "損壞",
    "missing": "遺失"
}

ITEM_TRANSLATIONS = {
    "Door": "門",
    "Window": "窗戶",
    "AC": "冷氣",
    "Air Conditioner": "冷氣",
    "Bed": "床",
    "Desk": "書桌",
    "Chair": "椅子",
    "Wardrobe": "衣櫃",
    "Light": "電燈",
    "Curtain": "窗簾",
    "Socket": "插座",
    "Mirror": "鏡子",
    "Trash Can": "垃圾桶",
    "Fan": "電風扇",
    "Table": "桌子",
    "Shelf": "架子",
    "Cabinet": "櫃子"
}

# Register Chinese font
try:
    font_name = 'ChineseFont'
    # 1. Try to load NotoSansCJKtc-Regular.ttf from the same directory
    font_path = os.path.join(os.path.dirname(__file__), 'NotoSansCJKtc-Regular.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont(font_name, font_path))
    else:
        # 2. If not found, try to load common Windows Chinese fonts
        win_font_paths = [
            "C:/Windows/Fonts/msjh.ttc", # Microsoft JhengHei
            "C:/Windows/Fonts/msjh.ttf",
            "C:/Windows/Fonts/msyh.ttc", # Microsoft YaHei
            "C:/Windows/Fonts/msyh.ttf",
            "C:/Windows/Fonts/simsun.ttc", # SimSun
            "C:/Windows/Fonts/mingliu.ttc" # MingLiU
        ]
        font_loaded = False
        for path in win_font_paths:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, path))
                    logger.info(f"Successfully loaded Chinese font from: {path}")
                    font_loaded = True
                    break
                except Exception as font_err:
                    logger.warning(f"Failed to load font from {path}: {font_err}")
        
        if not font_loaded:
            # 3. Fallback to Helvetica if no suitable Chinese font is found
            font_name = 'Helvetica'
            logger.warning(f"Warning: No suitable Chinese font found. Chinese characters may not render correctly. Using {font_name}.")
            # Helvetica is a built-in font, no need to register it with TTFont
    
    # Create styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Chinese', fontName=font_name, fontSize=12, leading=14))
    styles.add(ParagraphStyle(name='ChineseHeading1', fontName=font_name, fontSize=18, leading=22, spaceAfter=12, alignment=1))
    styles.add(ParagraphStyle(name='ChineseHeading2', fontName=font_name, fontSize=14, leading=18, spaceAfter=6))

except Exception as e:
    logger.error(f"Error registering font for PDF generation: {e}")
    # Fallback to basic Helvetica styles if any error occurs
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Chinese', fontName='Helvetica', fontSize=12, leading=14))
    styles.add(ParagraphStyle(name='ChineseHeading1', fontName='Helvetica', fontSize=18, leading=22, spaceAfter=12, alignment=1))
    styles.add(ParagraphStyle(name='ChineseHeading2', fontName='Helvetica', fontSize=14, leading=18, spaceAfter=6))


async def generate_inspection_pdf_report(inspections: List[Dict[str, Any]]) -> io.BytesIO:
    buffer = io.BytesIO()
    
    # Define custom page template for Header and Footer
    def header_footer(canvas, doc):
        canvas.saveState()
        
        # Header
        canvas.setFont(font_name, 10)
        canvas.drawString(inch/2, 11 * inch, "宿舍檢查管理系統")
        canvas.drawRightString(8 * inch, 11 * inch, f"產生時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        canvas.line(inch/2, 10.9 * inch, 8 * inch, 10.9 * inch)
        
        # Footer
        canvas.setFont(font_name, 9)
        canvas.drawString(inch/2, 0.75 * inch, "本報告由系統自動產生")
        canvas.drawRightString(8 * inch, 0.75 * inch, f"第 {doc.page} 頁")
        canvas.line(inch/2, 0.85 * inch, 8 * inch, 0.85 * inch)
        
        canvas.restoreState()

    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=inch/2, 
        leftMargin=inch/2, 
        topMargin=1.2*inch, 
        bottomMargin=1*inch
    )
    
    story = []

    # Title
    story.append(Paragraph("宿舍檢查報告", styles['ChineseHeading1']))
    story.append(Spacer(1, 0.3 * inch))

    for idx, inspection in enumerate(inspections):
        # Inspection Header Info Table
        info_data = [
            [f"檢查紀錄 ID: {inspection.get('id', 'N/A')}", ""],
            [f"提交時間: {inspection.get('submitted_at', 'N/A')}", f"學生姓名: {inspection.get('student', {}).get('full_name', 'N/A')}"],
            [f"寢室號碼: {inspection.get('room', {}).get('room_number', 'N/A')} / {inspection.get('student', {}).get('bed', {}).get('bed_number', 'N/A')}", ""],
        ]
        
        status_en = inspection.get('status', 'N/A')
        status_cn = STATUS_TRANSLATIONS.get(status_en, status_en)
        
        # Status Color Logic
        status_color = colors.black
        if status_en == 'approved': status_color = colors.green
        elif status_en == 'rejected': status_color = colors.red
        elif status_en == 'pending': status_color = colors.orange

        story.append(Paragraph(f"總體狀態: <font color={status_color}>{status_cn}</font>", styles['ChineseHeading2']))
        story.append(Spacer(1, 0.1 * inch))

        # Info Table Style
        info_table = Table(info_data, colWidths=[3.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)), # Span ID across both columns
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkslategray),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Details Table
        story.append(Paragraph("檢查詳情:", styles['ChineseHeading2']))
        data = [['項目', '狀態', '備註', '照片數']]
        
        row_colors = []
        
        for i, detail in enumerate(inspection.get('details', [])):
            item_name_en = detail.get('item', {}).get('name', 'N/A')
            item_name_cn = ITEM_TRANSLATIONS.get(item_name_en, item_name_en)
            status_text_en = detail.get('status', 'N/A')
            status_text_cn = STATUS_TRANSLATIONS.get(status_text_en, status_text_en)
            comment = detail.get('comment', '')
            photos_count = len(detail.get('photos', []))
            photos_info = f"{photos_count}" if photos_count > 0 else "-"
            
            data.append([item_name_cn, status_text_cn, comment, photos_info])
            
            # Alternate row colors
            if i % 2 == 0:
                row_colors.append(colors.whitesmoke)
            else:
                row_colors.append(colors.white)

        table = Table(data, colWidths=[1.5*inch, 1.2*inch, 3.3*inch, 1*inch])
        
        # Base Table Style
        tbl_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.2, 0.2)), # Dark Header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'), # Align comments to left
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, 0), 11), # Header Font Size
            ('FONTSIZE', (0, 1), (-1, -1), 10), # Body Font Size
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]

        # Apply Zebra Striping
        for i, color in enumerate(row_colors):
            tbl_style.append(('BACKGROUND', (0, i+1), (-1, i+1), color))

        table.setStyle(TableStyle(tbl_style))
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

        # Signature
        if inspection.get('signature'):
            story.append(Paragraph("學生簽名:", styles['ChineseHeading2']))
            if inspection['signature'].startswith('data:image'):
                try:
                    img_data = inspection['signature'].split(',')[1]
                    img_buffer = io.BytesIO(base64.b64decode(img_data))
                    img = Image(img_buffer)
                    img._restrictSize(2 * inch, 0.8 * inch)
                    story.append(img)
                except Exception as e:
                    story.append(Paragraph(f"簽名載入失敗", styles['Chinese']))
            story.append(Spacer(1, 0.2 * inch))

        # Separator (Page Break if not last item)
        if idx < len(inspections) - 1:
            from reportlab.platypus import PageBreak
            story.append(PageBreak())

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)
    return buffer
