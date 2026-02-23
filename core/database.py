from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import DB_PATH
from core.models import Base, Category, Expense

def get_engine():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(
        f"sqlite:///{DB_PATH}",
        connect_args={"check_same_thread": False},
        echo = False,
    )
    return engine

def init_db(engine=None):
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(engine)
    _seed_default_categories(engine)
    return engine

def _seed_default_categories(engine):
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text

    Session = sessionmaker(bind=engine)
    with Session() as session:
        count = session.query(Category).count()
        if count > 0:
            return
        
        defaults = [
            ("cat_1", "Alimentação", "#22c55e", True),
            ("cat_2", "Transporte", "#3b82f6", True),
            ("cat_3", "Moradia", "#8b5cf6", True),
            ("cat_4", "Saúde", "#ef4444", True),
            ("cat_5", "Lazer", "#f59e0b", True),
            ("cat_6", "Compras", "#ec4899", True),
            ("cat_7", "Outros", "#64748b", True),
        ]

        for cid, name, color, is_system in defaults:
            cat = Category(id=cid, name=name, color=color, is_system=is_system)
            session.add(cat)
        session.commit()

@contextmanager
def session_scope(engine=None):
    eng = engine or get_engine()
    SessionLocal = sessionmaker(
        bind=eng,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
