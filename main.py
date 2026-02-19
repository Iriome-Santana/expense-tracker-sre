from fastapi import FastAPI
from expenses import ExpenseManager
from pydantic import BaseModel

app = FastAPI()

class ExpenseCreate(BaseModel):
    date: str
    description: str
    amount: float
    
@app.get("/")
def home():
    return {"message": "Welcome to the Expense Tracker API!"}

@app.get("/expenses")
def get_expenses():
    manager = ExpenseManager()
    return manager.show_expenses()

@app.post("/expenses")
def create_expense(expense: ExpenseCreate):
    manager = ExpenseManager()
    manager.add_expense(expense.date, expense.description, expense.amount)
    return {"message": "Expense added successfully!"}

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    manager = ExpenseManager()
    manager.delete_expense(expense_id)
    return {"message": "Expense deleted successfully!"}

@app.get("/expenses/summary")
def get_summary():
    manager = ExpenseManager()
    total = manager.summary()
    return {"total": total}
