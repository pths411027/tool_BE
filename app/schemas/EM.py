# for development
from sqlite3 import Time
from sqlalchemy import Column, Date, ForeignKey, Integer, String

from app.database.sqlalchemy import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Expense(Base):
    __tablename__ = "EM_expense"
    expense_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    expense_name = Column(String(255), primary_key=False, index=True)
    expense_type = Column(String(255), index=False)
    expense_amount = Column(Integer, index=False)
    expense_time = Column(Integer, index=False)
