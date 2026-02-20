"""Business logic for expenses."""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from core.database import session_scope
from core import repository as repo


def add_expense(
    amount: Decimal,
    date: datetime,
    category_id: str,
    description: str = "",
    source: str = "",
):
    with session_scope() as session:
        return repo.create_expense(
            session, amount, date, category_id, description, source
        )


def list_expenses(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    category_id: Optional[str] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    source: Optional[str] = None,
    limit: Optional[int] = None,
):
    with session_scope() as session:
        return repo.get_expenses(
            session,
            date_from=date_from,
            date_to=date_to,
            category_id=category_id,
            min_amount=min_amount,
            max_amount=max_amount,
            source=source,
            limit=limit,
        )


def get_expense(expense_id: str):
    with session_scope() as session:
        return repo.get_expense_by_id(session, expense_id)


def update_expense(
    expense_id: str,
    amount: Optional[Decimal] = None,
    date: Optional[datetime] = None,
    category_id: Optional[str] = None,
    description: Optional[str] = None,
    source: Optional[str] = None,
):
    with session_scope() as session:
        return repo.update_expense(
            session,
            expense_id,
            amount=amount,
            date=date,
            category_id=category_id,
            description=description,
            source=source,
        )


def remove_expense(expense_id: str) -> bool:
    with session_scope() as session:
        return repo.delete_expense(session, expense_id)


def total_by_category(date_from: datetime, date_to: datetime):
    with session_scope() as session:
        return repo.get_total_by_category_in_period(session, date_from, date_to)


def monthly_totals(months_back: int = 12):
    with session_scope() as session:
        return repo.get_monthly_totals(session, months_back)


def total_spent(date_from: datetime, date_to: datetime) -> Decimal:
    with session_scope() as session:
        return repo.get_total_spent_in_period(session, date_from, date_to)
