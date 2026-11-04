import io
from datetime import timezone
from decimal import Decimal
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.order import Order, OrderStatus


class InvalidOrderStatusForReceiptError(Exception):
    """Raised when attempting to generate a receipt for a non-completed order."""
    pass


class ReceiptService:
    """
    Authoritative PDF receipt generation service for PayPilot AI.
    Strictly restricted to verified COMPLETED orders.
    """

    NAVY = colors.HexColor("#102A43")
    BLUE = colors.HexColor("#0070E0")
    SLATE = colors.HexColor("#526174")
    MUTED_BG = colors.HexColor("#F7F8FA")
    BORDER = colors.HexColor("#DCE3EA")
    PAID_GREEN = colors.HexColor("#0F5132")
    PAID_BG = colors.HexColor("#D1E7DD")

    @classmethod
    def generate_order_receipt_pdf(cls, order: Order) -> bytes:
        if order.status != OrderStatus.COMPLETED:
            raise InvalidOrderStatusForReceiptError(
                f"Receipts can only be generated for COMPLETED transactions. "
                f"Order '{order.id}' is in status '{order.status}'."
            )

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        brand_header_style = ParagraphStyle(
            "BrandHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=cls.NAVY,
        )

        meta_label_style = ParagraphStyle(
            "MetaLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=cls.SLATE,
        )

        meta_val_style = ParagraphStyle(
            "MetaVal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=cls.NAVY,
        )

        table_header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=cls.NAVY,
        )

        table_body_style = ParagraphStyle(
            "TableBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=cls.NAVY,
        )

        table_body_right = ParagraphStyle(
            "TableBodyRight",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=cls.NAVY,
            alignment=2,  # Right align
        )

        elements = []

        # 1. Header Banner
        header_table = Table(
            [
                [
                    Paragraph("<b>PayPilot AI</b>", brand_header_style),
                    Paragraph(
                        "<b>SETTLEMENT RECEIPT • OFFICIAL</b>",
                        ParagraphStyle(
                            "StatusBadge",
                            parent=styles["Normal"],
                            fontName="Helvetica-Bold",
                            fontSize=9,
                            leading=11,
                            textColor=cls.BLUE,
                            alignment=2,
                        ),
                    ),
                ]
            ],
            colWidths=[270, 270],
        )
        header_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        elements.append(header_table)

        elements.append(HRFlowable(width="100%", thickness=1, color=cls.BORDER, spaceAfter=14))

        # 2. Metadata Grid
        created_str = (
            order.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            if order.created_at
            else "N/A"
        )
        paypal_order = order.paypal_order_id or "N/A"
        paypal_capture = order.paypal_capture_id or "N/A"

        meta_data = [
            [
                Paragraph("INTERNAL ORDER ID", meta_label_style),
                Paragraph("PAYPAL ORDER ID", meta_label_style),
            ],
            [
                Paragraph(f"<b>{order.id}</b>", meta_val_style),
                Paragraph(f"<b>{paypal_order}</b>", meta_val_style),
            ],
            [
                Paragraph("DATE & TIME", meta_label_style),
                Paragraph("PAYPAL CAPTURE ID", meta_label_style),
            ],
            [
                Paragraph(created_str, meta_val_style),
                Paragraph(f"<b>{paypal_capture}</b>", meta_val_style),
            ],
            [
                Paragraph("PAYMENT STATUS", meta_label_style),
                Paragraph("PAYMENT METHOD", meta_label_style),
            ],
            [
                Paragraph(
                    f"<font color='{cls.PAID_GREEN.hexval()}'><b>COMPLETED (PAID)</b></font>",
                    meta_val_style,
                ),
                Paragraph("PayPal Orders v2 REST API (Sandbox)", meta_val_style),
            ],
        ]

        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        elements.append(meta_table)

        elements.append(Spacer(1, 14))
        elements.append(HRFlowable(width="100%", thickness=1, color=cls.BORDER, spaceAfter=12))

        # 3. Line Items Table
        items_data = [
            [
                Paragraph("ITEM DESCRIPTION", table_header_style),
                Paragraph("SKU", table_header_style),
                Paragraph("QTY", table_header_style),
                Paragraph("UNIT PRICE", ParagraphStyle("THRight", parent=table_header_style, alignment=2)),
                Paragraph("TOTAL", ParagraphStyle("THRight2", parent=table_header_style, alignment=2)),
            ]
        ]

        subtotal = Decimal("0.00")
        for item in order.items:
            u_price = Decimal(str(item.unit_price))
            t_price = Decimal(str(item.total_price))
            subtotal += t_price
            items_data.append([
                Paragraph(f"<b>{item.name}</b>", table_body_style),
                Paragraph(item.sku, table_body_style),
                Paragraph(str(item.quantity), table_body_style),
                Paragraph(f"${u_price:.2f}", table_body_right),
                Paragraph(f"${t_price:.2f}", table_body_right),
            ])

        items_table = Table(
            items_data,
            colWidths=[210, 100, 45, 90, 95],
        )
        items_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), cls.MUTED_BG),
                ("TEXTCOLOR", (0, 0), (-1, 0), cls.NAVY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), 1, cls.BORDER),
                ("LINEBELOW", (0, 1), (-1, -1), 0.5, cls.BORDER),
            ])
        )
        elements.append(items_table)

        elements.append(Spacer(1, 12))

        # 4. Totals Block
        total_amount = Decimal(str(order.total_amount))
        totals_data = [
            [
                "",
                Paragraph("Items Subtotal:", meta_val_style),
                Paragraph(f"${subtotal:.2f} {order.currency}", table_body_right),
            ],
            [
                "",
                Paragraph("Estimated Tax (Sandbox):", meta_val_style),
                Paragraph(f"$0.00 {order.currency}", table_body_right),
            ],
            [
                "",
                Paragraph("<b>Total Amount Paid:</b>", ParagraphStyle("TB", parent=meta_val_style, fontSize=11, leading=14)),
                Paragraph(
                    f"<b>${total_amount:.2f} {order.currency}</b>",
                    ParagraphStyle("TBAmount", parent=table_body_right, fontSize=12, leading=14, textColor=cls.NAVY),
                ),
            ],
        ]

        totals_table = Table(totals_data, colWidths=[290, 130, 120])
        totals_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LINEABOVE", (1, 2), (2, 2), 1, cls.BORDER),
            ])
        )
        elements.append(KeepTogether(totals_table))

        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=1, color=cls.BORDER, spaceAfter=10))

        # 5. Security & Settlement Footer
        footer_style = ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=cls.SLATE,
        )
        footer_text = (
            f"<b>Security & Audit Trail:</b> This document serves as an immutable, server-verified settlement receipt. "
            f"Payment capture was processed and verified via PayPal Orders v2 REST API under idempotency key "
            f"<code>{order.capture_idempotency_key[:16]}...</code>. "
            f"All item prices and inventory movements were recorded atomically in the merchant database."
        )
        elements.append(Paragraph(footer_text, footer_style))

        doc.build(elements)
        return buffer.getvalue()

