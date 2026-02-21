"""Business logic for categories and limits."""
from decimal import Decimal
from typing import Optional

from core.database import session_scope
from core import repository as repo


def list_categories():
    with session_scope() as session:
        return repo.get_all_categories(session)


def get_category(category_id: str):
    with session_scope() as session:
        return repo.get_category_by_id(session, category_id)
    
def get_category_color(category_id: str) -> Optional[str]:
    with session_scope() as session:
        cat = repo.get_category_by_id(session, category_id)
        return cat.color

def create_category(
    name: str,
    color: str = "#6366f1",
    icon: str = "",
    monthly_limit: Optional[Decimal] = None,
):
    with session_scope() as session:
        return repo.create_category(
            session, name, color=color, icon=icon, monthly_limit=monthly_limit
        )


def update_category(
    category_id: str,
    name: Optional[str] = None,
    color: Optional[str] = None,
    monthly_limit: Optional[Decimal] = None,
):
    with session_scope() as session:
        return repo.update_category(
            session, category_id, name=name, color=color, monthly_limit=monthly_limit
        )


def delete_category(category_id: str) -> bool:
    with session_scope() as session:
        return repo.delete_category(session, category_id)


def set_limit_for_month(category_id: str, year_month: str, limit_value: Decimal):
    """year_month format: YYYY-MM."""
    with session_scope() as session:
        return repo.set_category_limit_for_month(
            session, category_id, year_month, limit_value
        )


def get_limit_for_month(category_id: str, year_month: str):
    with session_scope() as session:
        return repo.get_category_limit_for_month(session, category_id, year_month)
