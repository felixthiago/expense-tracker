"""Export expenses to CSV and PDF."""
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional

from app.config import EXPORTS_DIR
from services.expense_service import list_expenses


def _ensure_exports_dir():
    Path(EXPORTS_DIR).mkdir(parents=True, exist_ok=True)


def export_csv(
    filepath: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    category_id: Optional[str] = None,
) -> str:
    _ensure_exports_dir()
    if not filepath:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = str(Path(EXPORTS_DIR) / f"despesas_{ts}.csv")

    expenses = list_expenses(
        date_from=date_from, date_to=date_to, category_id=category_id
    )

    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        f.write("Data;Valor;Categoria;Descrição;Origem\n")
        for e in expenses:
            date_str = e.date.strftime("%Y-%m-%d") if e.date else ""
            amount_str = str(e.amount).replace(".", ",")
            cat_name = e.category.name if e.category else ""
            desc = (e.description or "").replace(";", ",").replace("\n", " ")
            source = e.source or ""
            f.write(f"{date_str};{amount_str};{cat_name};{desc};{source}\n")

    return filepath


def export_pdf(
    filepath: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    category_id: Optional[str] = None,
) -> str:
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:
        raise RuntimeError("reportlab não instalado. Execute: pip install reportlab")

    _ensure_exports_dir()
    if not filepath:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = str(Path(EXPORTS_DIR) / f"despesas_{ts}.pdf")

    expenses = list_expenses(
        date_from=date_from, date_to=date_to, category_id=category_id
    )

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=12,
    )

    flow = []
    flow.append(Paragraph("Relatório de Despesas", title_style))
    if date_from or date_to:
        period = []
        if date_from:
            period.append(date_from.strftime("%d/%m/%Y"))
        if date_to:
            period.append(date_to.strftime("%d/%m/%Y"))
        flow.append(Paragraph(f"Período: {' a '.join(period)}", styles["Normal"]))
    flow.append(Spacer(1, 0.5 * cm))

    if not expenses:
        flow.append(Paragraph("Nenhuma despesa no período.", styles["Normal"]))
    else:
        data = [["Data", "Valor (R$)", "Categoria", "Descrição", "Origem"]]
        total = Decimal("0")
        for e in expenses:
            date_str = e.date.strftime("%d/%m/%Y") if e.date else ""
            amount_str = f"{e.amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            cat_name = e.category.name if e.category else ""
            desc = (e.description or "")[:40]
            source = e.source or ""
            data.append([date_str, amount_str, cat_name, desc, source])
            total += e.amount
        data.append(["", f"Total: {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), "", "", ""])

        table = Table(data, colWidths=[2 * cm, 2.5 * cm, 3 * cm, 6 * cm, 2.5 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366f1")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("TOPPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -2), colors.white),
                    ("GRID", (0, 0), (-1, -2), 0.5, colors.lightgrey),
                    ("LINEABOVE", (0, -1), (-1, -1), 1, colors.grey),
                    ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ]
            )
        )
        flow.append(table)

    doc.build(flow)
    return filepath
