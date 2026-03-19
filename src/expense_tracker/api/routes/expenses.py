import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from expense_tracker.db.session import get_db
from expense_tracker.schemas.expense import ExpenseCreate, ExpenseResponse
from expense_tracker.services.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    total = ExpenseService().summary(db)
    logging.info(f"Summary requested - total: {total}")
    return {"total": total}


@router.get("/", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    expenses = ExpenseService().show_expenses(db)
    logging.info(f"Expenses listed - count: {len(expenses)}")
    return expenses


@router.post("/", status_code=201)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    ExpenseService().add_expense(db, expense.date, expense.description, expense.amount)
    logging.info(f"Expense created - date: {expense.date}, description: {expense.description}, amount: {expense.amount}")
    return {"message": "Expense added successfully!"}


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    ExpenseService().delete_expense(db, expense_id)
    logging.info(f"Expense deleted - id: {expense_id}")
    return {"message": "Expense deleted successfully!"}