from functools import wraps
from datetime import datetime, date as date_type

from sqlalchemy.orm import Session

from expense_tracker.models.expense import Expense
from expense_tracker.core.errors import FieldsRequiredError, NegativeAmountError, ExpenseNotFoundError


def validate_expense(func):
    @wraps(func)
    def wrapper_inner(self, db: Session, *args, **kwargs):
        date = args[0]
        description = args[1]
        amount = args[2]
        if not date or not description:
            raise FieldsRequiredError()
        if amount <= 0:
            raise NegativeAmountError()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        if amount <= 0:
            raise NegativeAmountError("Amount must be greater than 0")
        return func(self, db, *args, **kwargs)

    return wrapper_inner


class ExpenseService:
    """Business logic for expense management."""

    @validate_expense
    def add_expense(self, db: Session, date: str, description: str, amount: float, owner: str = "default"):
        expense = Expense(
            date=datetime.strptime(date, "%Y-%m-%d").date(),
            description=description,
            amount=amount,
            owner=owner
        )
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense

    def show_expenses(self, db: Session, owner: str = "default") -> list[Expense]:
        return db.query(Expense).filter(Expense.owner == owner).all()

    def delete_expense(self, db: Session, expense_id: int, owner: str = "default"):
        expense = db.query(Expense).filter(
            Expense.id == expense_id, 
            Expense.owner == owner
            ).first()
        if not expense:
            raise ExpenseNotFoundError(expense_id)
        db.delete(expense)
        db.commit()

    def summary(self, db: Session, owner: str = "default") -> float:
        expenses = db.query(Expense).filter(Expense.owner == owner).all()
        return float(sum(e.amount for e in expenses))