import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from expense_tracker.core.errors import NegativeAmountError, FieldsRequiredError, ExpenseNotFoundError
from tests.conftest import make_expense


# --- add expense ---

def test_add_expense(service, db):
    service.add_expense(db, "2026-01-27", "Coffee", 3.5)
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_add_expense_amount_negative(service, db):
    with pytest.raises(NegativeAmountError):
        service.add_expense(db, "2026-01-27", "Coffee", -3.5)


def test_add_expense_amount_zero(service, db):
    with pytest.raises(NegativeAmountError):
        service.add_expense(db, "2026-01-27", "Coffee", 0)


def test_add_expense_empty_fields(service, db):
    with pytest.raises(FieldsRequiredError):
        service.add_expense(db, "", "", 0)


def test_add_expense_invalid_date(service, db):
    with pytest.raises(ValueError):
        service.add_expense(db, "27-01-2026", "Coffee", 3.5)


# --- show expenses ---

def test_show_expenses(service, db):
    expense = make_expense()
    db.query.return_value.all.return_value = [expense]
    result = service.show_expenses(db)
    assert len(result) == 1
    assert result[0].description == "Coffee"


def test_show_expenses_empty(service, db):
    db.query.return_value.all.return_value = []
    assert service.show_expenses(db) == []


# --- delete expense ---

def test_delete_expense(service, db):
    expense = make_expense()
    db.query.return_value.filter.return_value.first.return_value = expense
    service.delete_expense(db, 1)
    db.delete.assert_called_once_with(expense)
    db.commit.assert_called_once()


def test_delete_expense_not_found(service, db):
    db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ExpenseNotFoundError):
        service.delete_expense(db, 999)


# --- summary ---

def test_summary(service, db):
    expenses = [make_expense(amount="3.5"), make_expense(amount="1.5")]
    db.query.return_value.all.return_value = expenses
    assert service.summary(db) == 5.0


def test_summary_empty(service, db):
    db.query.return_value.all.return_value = []
    assert service.summary(db) == 0.0