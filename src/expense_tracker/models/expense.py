from sqlalchemy import Column, Integer, Date, Text, Numeric, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    owner = Column(String, nullable=False)
