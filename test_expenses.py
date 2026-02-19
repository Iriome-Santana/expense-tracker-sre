import pytest
from unittest.mock import patch
from expenses import ExpenseManager
from errors import NegativeAmountError, FieldsRequiredError

"""fixture"""
@pytest.fixture
def manager_mock():
    fake_db = []
    
    def fake_add(date, description, amount):
        fake_db.append({"date": date, "description": description, "amount": amount})

    def fake_delete(expense_id):
        if expense_id >= len(fake_db) or not fake_db:
            raise ValueError("Expense not found")
        fake_db.pop(expense_id)
    
    with patch("expenses.load_expenses", side_effect=lambda: fake_db), \
         patch("expenses.add_expense", side_effect=fake_add), \
         patch("expenses.delete_expense", side_effect=fake_delete):
        manager = ExpenseManager()
        yield manager


"""add expense tests"""
def test_add_expense_fixture(manager_mock):
    initial_count = len(manager_mock.show_expenses())
    
    manager_mock.add_expense("2026-01-27", "Coffee", 3.5)
    
    assert len(manager_mock.show_expenses()) == initial_count + 1
    assert manager_mock.show_expenses()[-1]["description"] == "Coffee"
    assert manager_mock.show_expenses()[-1]["amount"] == 3.5
    
def test_add_expense_amount_negative(manager_mock):
    with pytest.raises(NegativeAmountError):
        manager_mock.add_expense("2026-01-27", "Coffee", -3.5)
        
def test_add_expense_amount_zero(manager_mock):
    with pytest.raises(FieldsRequiredError):
        manager_mock.add_expense("2026-01-27", "Coffee", 0)
        
def test_add_expense_empty_fields(manager_mock):
    with pytest.raises(FieldsRequiredError):
        manager_mock.add_expense("", "", 0)

"""show expenses tests"""
def test_show_expenses_fixture(manager_mock):
    manager_mock.add_expense("2026-01-27", "Coffee", 3.5)
    assert manager_mock.show_expenses() == [{"date": "2026-01-27", "description": "Coffee", "amount": 3.5}]

def test_show_expenses_empty(manager_mock):
    assert manager_mock.show_expenses() == []

"""delete expense tests"""
def test_delete_expense_fixture(manager_mock):
    manager_mock.add_expense("2026-01-27", "Coffee", 3.5)
    manager_mock.delete_expense(0)
    assert len(manager_mock.show_expenses()) == 0

def test_delete_expense_invalid_index(manager_mock):
    with pytest.raises(ValueError):
        manager_mock.delete_expense(0)
        
def test_delete_expense_no_expenses(manager_mock):
    with pytest.raises(ValueError):
        manager_mock.delete_expense(0)
        
"""summary tests"""
def test_summary_fixture(manager_mock):
    manager_mock.add_expense("2026-01-27", "Coffee", 3.5)
    assert manager_mock.summary() == 3.5