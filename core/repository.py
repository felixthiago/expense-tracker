"""Data access layer for expenses and categories."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.models import Category, CategoryLimit, Expense


def _uuid():
    return str(uuid.uuid4())

# ---------- Categories ----------

def get_all_categories(session: Session) -> list[Category]:
    return session.query(Category).order_by(Category.name).all()


def get_category_by_id(session: Session, category_id: str) -> Optional[Category]:
    return session.query(Category).filter(Category.id == category_id).first()


def get_category_by_name(session: Session, name: str) -> Optional[Category]:
    return session.query(Category).filter(Category.name == name).first()


def create_category(
    session: Session,
    name: str,
    color: str = "#6366f1",
    icon: str = "",
    monthly_limit: Optional[Decimal] = None,
) -> Category:
    cat = Category(
        id=_uuid(),
        name=name.strip(),
        color=color,
        icon=icon,
        monthly_limit=monthly_limit,
        is_system=False,
    )
    session.add(cat)
    session.flush()
    return cat


def update_category(
    session: Session,
    category_id: str,
    name: Optional[str] = None,
    color: Optional[str] = None,
    monthly_limit: Optional[Decimal] = None,
) -> Optional[Category]:
    cat = get_category_by_id(session, category_id)
    if not cat:
        return None
    if name is not None:
        cat.name = name.strip()
    if color is not None:
        cat.color = color
    if monthly_limit is not None:
        cat.monthly_limit = monthly_limit
    return cat


def delete_category(session: Session, category_id: str) -> bool:
    cat = get_category_by_id(session, category_id)
    if not cat or cat.is_system:
        return False
    session.delete(cat)
    return True


def set_category_limit_for_month(
    session: Session, category_id: str, year_month: str, limit_value: Decimal
) -> CategoryLimit:
    """Set or update spending limit for a category in a given month (YYYY-MM)."""
    existing = (
        session.query(CategoryLimit)
        .filter(
            CategoryLimit.category_id == category_id,
            CategoryLimit.month == year_month,
        )
        .first()
    )
    if existing:
        existing.limit_value = limit_value
        return existing
    limit = CategoryLimit(
        id=_uuid(),
        category_id=category_id,
        month=year_month,
        limit_value=limit_value,
    )
    session.add(limit)
    session.flush()
    return limit


def get_category_limit_for_month(
    session: Session, category_id: str, year_month: str
) -> Optional[CategoryLimit]:
    return (
        session.query(CategoryLimit)
        .filter(
            CategoryLimit.category_id == category_id,
            CategoryLimit.month == year_month,
        )
        .first()
    )


# ---------- Expenses ----------


def create_expense(
    session: Session,
    amount: Decimal,
    date: datetime,
    category_id: str,
    description: str = "",
    source: str = "",
) -> Expense:
    exp = Expense(
        id=_uuid(),
        amount=amount,
        date=date,
        category_id=category_id,
        description=description.strip(),
        source=source.strip(),
    )
    session.add(exp)
    session.flush()
    return exp


def get_expense_by_id(session: Session, expense_id: str) -> Optional[Expense]:
    return session.query(Expense).filter(Expense.id == expense_id).first()


def get_expenses(
    session: Session,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    category_id: Optional[str] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    source: Optional[str] = None,
    limit: Optional[int] = None,
) -> list[Expense]:
    q = session.query(Expense).order_by(Expense.date.desc(), Expense.created_at.desc())
    if date_from:
        q = q.filter(Expense.date >= date_from)
    if date_to:
        q = q.filter(Expense.date <= date_to)
    if category_id:
        q = q.filter(Expense.category_id == category_id)
    if min_amount is not None:
        q = q.filter(Expense.amount >= min_amount)
    if max_amount is not None:
        q = q.filter(Expense.amount <= max_amount)
    if source:
        q = q.filter(Expense.source.ilike(f"%{source}%"))
    if limit:
        q = q.limit(limit)
    return q.all()


def update_expense(
    session: Session,
    expense_id: str,
    amount: Optional[Decimal] = None,
    date: Optional[datetime] = None,
    category_id: Optional[str] = None,
    description: Optional[str] = None,
    source: Optional[str] = None,
) -> Optional[Expense]:
    exp = get_expense_by_id(session, expense_id)
    if not exp:
        return None
    if amount is not None:
        exp.amount = amount if not None else exp.amount
    if date is not None:
        exp.date = date
    if category_id is not None:
        exp.category_id = category_id
    if description is not None:
        exp.description = description
    if source is not None:
        exp.source = source
    return exp


def delete_expense(session: Session, expense_id: str) -> bool:
    exp = get_expense_by_id(session, expense_id)
    if not exp:
        return False
    session.delete(exp)
    return True

CategoryTotal = tuple[str, str, Decimal]
def get_total_by_category_in_period(session: Session, date_from: datetime, date_to: datetime) -> list[CategoryTotal]:
    """return (category_id, category_name, total)"""
    q = (
        session.query(Category.id, Category.name, func.sum(Expense.amount).label("total"))
        .join(Expense, Expense.category_id == Category.id)
        .filter(Expense.date >= date_from, Expense.date <= date_to)
        .group_by(Category.id, Category.name)
    )
    return [(r.id, r.name, r.total or Decimal("0")) for r in q.all()]


def get_monthly_totals(session: Session, months_back: int = 12) -> list[tuple[str, Decimal]]:
    """return (year_month, total) for the last x months."""
    from datetime import date

    end = date.today()
    year, month = end.year, end.month
    month -= months_back
    while month <= 0:
        month += 12
        year -= 1
    start = date(year, month, 1)
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())

    subq = (
        session.query(
            func.strftime("%Y-%m", Expense.date).label("ym"),
            func.sum(Expense.amount).label("total"),
        )
        .filter(Expense.date >= start_dt, Expense.date <= end_dt)
        .group_by(func.strftime("%Y-%m", Expense.date))
    )
    rows = subq.all()
    return [(r.ym, r.total or Decimal("0")) for r in rows]


def get_total_spent_in_period(session: Session, date_from: datetime, date_to: datetime) -> Decimal:
    result = (
        session.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.date >= date_from, Expense.date <= date_to)
        .scalar()
    )
    return Decimal(str(result))
