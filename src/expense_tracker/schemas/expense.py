from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    date: str
    description: str
    amount: float


class ExpenseResponse(BaseModel):
    id: int
    date: date
    description: str
    amount: Decimal

    model_config = {"from_attributes": True}
