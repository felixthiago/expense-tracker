from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship

class Base(DeclarativeBase):
    pass

class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    color = Column(String(7), default="#6366f1")
    icon = Column(String(50), default="")
    monthly_limit = Column(Numeric(15, 2), nullable=True) 
    is_system = Column(Boolean, default = False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    expenses = relationship("Expense", back_populates="category", cascade="all, delete-orphan")
    limits = relationship("CategoryLimit", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category {self.name}>"

class CategoryLimit(Base):
    __tablename__ = "category_limits"

    id = Column(String(36), primary_key=True)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    limit_value = Column(Numeric(15, 2), nullable=False)
    month = Column(String(7), nullable=False)  # YYYY-MM
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="limits")

    def __repr__(self):
        return f"<CategoryLimit category={self.category_id} month={self.month}>"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String(36), primary_key=True)
    amount = Column(Numeric(15, 2), nullable=False)
    date = Column(DateTime, nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False)
    description = Column(Text, default="")
    source = Column(String(50), default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="expenses")

    def __repr__(self):
        return f"<Expense {self.amount} {self.date.date()}>"
