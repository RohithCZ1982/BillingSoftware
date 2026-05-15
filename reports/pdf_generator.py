import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from config import BILLS_PDF_DIR


def generate_bill_pdf(bill_data: dict) -> str:
    """
    bill_data keys:
      bill_number, bill_date, school_name, class_name,
      student_name, student_section, parent_name, parent_phone,
      items: list of {name, size, category, quantity, unit_price, total_price},
      subtotal, discount_type, discount_value, grand_total, notes
    Returns the saved PDF file path.
    """
    # ── Load shop settings from DB ───────────────────────────────────────────
    from database.database import get_shop_settings
    s = get_shop_settings()
    shop_name    = s.shop_name    or "Uniform Shop"
    addr_line1   = s.address_line1 or ""
    addr_line2   = s.address_line2 or ""
    phone        = s.phone        or ""
    email        = s.email        or ""
    gst_number   = s.gst_number   or ""
    footer_note  = s.footer_note  or ""

    # Build address / contact line
    address_str = ", ".join(filter(None, [addr_line1, addr_line2]))
    contact_parts = []
    if phone:
        contact_parts.append(f"Ph: {phone}")
    if email:
        contact_parts.append(f"Email: {email}")
    if gst_number:
        contact_parts.append(f"GST: {gst_number}")
    contact_str = "  |  ".join(contact_parts)

    os.makedirs(BILLS_PDF_DIR, exist_ok=True)
    filename = f"{bill_data['bill_number'].replace('/', '_')}.pdf"
    filepath = os.path.join(BILLS_PDF_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
    )

    story = []

    # ── Header ──────────────────────────────────────────────────────────────
    shop_style = ParagraphStyle(
        "shop", fontSize=18, fontName="Helvetica-Bold",
        leading=24, alignment=TA_CENTER,
        spaceBefore=0, spaceAfter=6,
    )
    addr_style = ParagraphStyle(
        "addr", fontSize=9, fontName="Helvetica",
        leading=14, alignment=TA_CENTER,
        spaceBefore=0, spaceAfter=4,
    )
    story.append(Paragraph(shop_name, shop_style))
    if address_str:
        story.append(Paragraph(address_str, addr_style))
    if contact_str:
        story.append(Paragraph(contact_str, addr_style))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1a73e8")))
    story.append(Spacer(1, 4*mm))

    # ── Bill Info ────────────────────────────────────────────────────────────
    bill_date_str = bill_data["bill_date"]
    if isinstance(bill_date_str, datetime):
        bill_date_str = bill_date_str.strftime("%d-%m-%Y %I:%M %p")

    info_data = [
        ["Bill No:", bill_data["bill_number"], "Date:", bill_date_str],
        ["School:", bill_data.get("school_name", ""), "Class:", bill_data.get("class_name", "")],
        ["Student:", bill_data.get("student_name", ""), "Section:", bill_data.get("student_section", "")],
        ["Parent:", bill_data.get("parent_name", ""), "Phone:", bill_data.get("parent_phone", "")],
    ]
    info_table = Table(info_data, colWidths=[25*mm, 65*mm, 20*mm, 65*mm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 3*mm))

    # ── Items Table ──────────────────────────────────────────────────────────
    header = ["#", "Item Name", "Size", "Category", "Qty", "Unit Price (₹)", "Total (₹)"]
    table_data = [header]
    for i, item in enumerate(bill_data.get("items", []), 1):
        table_data.append([
            str(i),
            item.get("name", ""),
            item.get("size", "-"),
            item.get("category", ""),
            str(item.get("quantity", 1)),
            f"{item.get('unit_price', 0):.2f}",
            f"{item.get('total_price', 0):.2f}",
        ])

    col_widths = [10*mm, 55*mm, 18*mm, 25*mm, 12*mm, 28*mm, 27*mm]
    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a73e8")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (1, 1), (1, -1), "LEFT"),
        ("ALIGN", (3, 1), (3, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4ff")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 4*mm))

    # ── Totals ───────────────────────────────────────────────────────────────
    subtotal      = bill_data.get("subtotal", 0)
    discount_type = bill_data.get("discount_type", "flat")
    discount_value = bill_data.get("discount_value", 0)
    grand_total   = bill_data.get("grand_total", 0)

    if discount_type == "percent":
        discount_label  = f"Discount ({discount_value}%)"
        discount_amount = subtotal * discount_value / 100
    else:
        discount_label  = "Discount"
        discount_amount = discount_value

    totals_data = [
        ["", "", "Subtotal:", f"₹ {subtotal:.2f}"],
        ["", "", discount_label + ":", f"- ₹ {discount_amount:.2f}"],
        ["", "", "GRAND TOTAL:", f"₹ {grand_total:.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[50*mm, 60*mm, 45*mm, 30*mm])
    totals_table.setStyle(TableStyle([
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 2), (3, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("FONTSIZE", (2, 2), (3, 2), 12),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("TEXTCOLOR", (2, 2), (3, 2), colors.HexColor("#1a73e8")),
        ("BACKGROUND", (2, 2), (3, 2), colors.HexColor("#e8f0fe")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE", (2, 2), (3, 2), 1, colors.HexColor("#1a73e8")),
    ]))
    story.append(totals_table)

    # ── Bill notes ───────────────────────────────────────────────────────────
    if bill_data.get("notes"):
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph(
            f"<b>Notes:</b> {bill_data['notes']}",
            ParagraphStyle("notes", fontSize=8)
        ))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    footer_style = ParagraphStyle("footer", fontSize=8, alignment=TA_CENTER,
                                   textColor=colors.grey, leading=12)
    if footer_note:
        story.append(Paragraph(footer_note, footer_style))
    story.append(Paragraph(f"Generated by {shop_name} Billing System", footer_style))

    doc.build(story)
    return filepath
