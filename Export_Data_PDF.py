from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
import sqlite3
import os
from datetime import datetime
from reportlab.lib.units import mm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "expenses.db")
PDF_NAME = os.path.join(BASE_DIR, f"Expense_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

def export_to_pdf():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, account, amount, type, note, date FROM transactions ORDER BY date DESC")
    data = c.fetchall()
    conn.close()

    if not data:
        print("❌ No transactions found to export.")
        return

    # Calculate Summary
    income = sum(row[2] for row in data if row[3].lower() == 'income')
    expense = sum(row[2] for row in data if row[3].lower() == 'expense')
    balance = income - expense

    # Setup PDF
    doc = SimpleDocTemplate(PDF_NAME, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='TitleCenter', fontSize=22, alignment=TA_CENTER, textColor=colors.HexColor('#003366')))
    styles.add(ParagraphStyle(name='NormalBlue', textColor=colors.HexColor('#003366')))
    styles.add(ParagraphStyle(name='SummaryRight', alignment=TA_RIGHT, textColor=colors.HexColor('#002244'), fontSize=12))

    # Title
    title = Paragraph("Personal Expense Report", styles['TitleCenter'])
    date = Paragraph(f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", styles['NormalBlue'])

    # Summary Section
    summary = Paragraph(f"""
        <b>Total Income:</b> Rs. {income:,.2f}<br/>
        <b>Total Expense:</b> Rs. {expense:,.2f}<br/>
        <b>Balance:</b> Rs. {balance:,.2f}
    """, styles['SummaryRight'])

    elements.extend([title, Spacer(1, 12), date, Spacer(1, 12), summary, Spacer(1, 24)])

    # Table Headers
    table_data = [['S.No', 'Account', 'Amount (Rs)', 'Type', 'Note', 'Date']]
    for idx, row in enumerate(data, start=1):
        table_data.append([str(idx)] + list(map(str, row[1:])))

    # Table Styling
    table = Table(table_data, repeatRows=1, colWidths=[40, 80, 70, 60, 150, 90])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#003366')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),

        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),

        # Alternating row colors
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f8ff')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e6f2ff'), colors.white]),

        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#003366')),
    ]))

    elements.append(table)

    # Build PDF with page number footer
    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(200 * mm, 10 * mm, text)

    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

    print(f"✅ PDF report successfully created: {PDF_NAME}")
