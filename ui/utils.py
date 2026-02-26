from datetime import datetime
from decimal import Decimal

MESES = ("janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")

def _month_year_pt(dt: datetime) -> str:
    return f"{MESES[dt.month - 1]}, {dt.year}"

def _format_currency(value: Decimal) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def _safe_call(obj, method_name, *args, **kwargs):
    """no intuito de evitar erros do pylance, simplesmente chama o método se existir."""
    method = getattr(obj, method_name, None)
    if method:
        return method(*args, **kwargs)
