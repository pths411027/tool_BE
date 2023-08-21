# for development
from sqlalchemy import (JSON, TEXT, Boolean, Column, Date, Float, ForeignKey,
                        Index, Integer, String)

from app.database.sqlalchemy import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String(255), primary_key=False, index=True)
    user_password = Column(String(255), primary_key=False, index=False)
    user_email = Column(String(255), primary_key=False, index=False)
