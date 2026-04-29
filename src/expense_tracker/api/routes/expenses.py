import logging

from fastapi import APIRouter, Depends, Request
from prometheus_client import Counter, Gauge
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from expense_tracker.db.session import get_db
from expense_tracker.schemas.expense import ExpenseCreate, ExpenseResponse
from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.services.backup_service import backup_expenses

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/expenses", tags=["expenses"])

expenses_created_total = Counter(
    "expenses_created_total",
    "Total number of expenses created"
)

expenses_deleted_total = Counter(
    "expenses_deleted_total",
    "Total number of expenses deleted"
)

expenses_in_db = Gauge(
    "expenses_in_db",
    "Current number of expenses in the database"
)

expenses_amount_total = Gauge(
    "expenses_amount_total",
    "Current total amount of all expenses in the database"
)


@router.get("/summary")
@limiter.limit("60/minute")
def get_summary(request: Request, db: Session = Depends(get_db)):
    total = ExpenseService().summary(db)
    expenses_amount_total.set(total)
    logging.info(f"Summary requested - total: {total}")
    return {"total": total}


@router.get("/", response_model=list[ExpenseResponse])
@limiter.limit("60/minute")
def get_expenses(request: Request, db: Session = Depends(get_db)):
    expenses = ExpenseService().show_expenses(db)
    expenses_in_db.set(len(expenses))
    logging.info(f"Expenses listed - count: {len(expenses)}")
    return expenses


@router.post("/", status_code=201)
@limiter.limit("20/minute")
def create_expense(request: Request, expense: ExpenseCreate, db: Session = Depends(get_db)):
    ExpenseService().add_expense(db, expense.date, expense.description, expense.amount)
    expenses_created_total.inc()
    expenses_in_db.inc()
    backup_expenses(db)
    logging.info(f"Expense created - description: {expense.description} amount: {expense.amount}")
    return {"message": "Expense added successfully!"}


@router.delete("/{expense_id}")
@limiter.limit("20/minute")
def delete_expense(request: Request, expense_id: int, db: Session = Depends(get_db)):
    ExpenseService().delete_expense(db, expense_id)
    expenses_deleted_total.inc()
    expenses_in_db.dec()
    backup_expenses(db)
    logging.info(f"Expense deleted - id: {expense_id}")
    return {"message": "Expense deleted successfully!"}