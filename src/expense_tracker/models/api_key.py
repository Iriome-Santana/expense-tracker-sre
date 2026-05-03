from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from expense_tracker.models.expense import Base

class ApiKey(Base):
    __tablename__ = "api_keys"

    key = Column(String, primary_key=True)
    owner = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())