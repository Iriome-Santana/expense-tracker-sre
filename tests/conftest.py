import pytest
from unittest.mock import MagicMock
from decimal import Decimal
from datetime import date

from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.models.expense import Expense


def make_expense(id=1, date_str="2026-01-27", description="Coffee", amount="3.5"):
    e = Expense()
    e.id = id
    e.date = date.fromisoformat(date_str)
    e.description = description
    e.amount = Decimal(amount)
    return e


@pytest.fixture
def db():
    """Mock SQLAlchemy session."""
    return MagicMock()


@pytest.fixture
def service():
    return ExpenseService()
