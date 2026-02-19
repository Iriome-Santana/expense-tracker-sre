from storage import load_expenses, add_expense, delete_expense
from functools import wraps
from errors import *
from datetime import datetime



def validate_expense(func):
    @wraps(func)
    def wrapper_inner(self, *args, **kwargs):
        date = args[0]
        description = args[1]
        amount = args[2]
        if not date or not description or not amount:
            raise FieldsRequiredError("All fields are required")
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        if amount <= 0:
            raise NegativeAmountError("Amount must be greater than 0")
        return func(self, *args, **kwargs)
    return wrapper_inner

class ExpenseManager:
    """Expense manager class"""
    
    
    @validate_expense
    def add_expense(self, date: str, description: str, amount: float):        
        add_expense(date, description, amount)
    
    def show_expenses(self) -> list:
        return load_expenses()
    

    def delete_expense(self, expense_id: int):
        delete_expense(expense_id)

    def summary(self) -> float:
        total = sum(expense["amount"] for expense in load_expenses())
        return total
