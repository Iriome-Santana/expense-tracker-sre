import os
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from expense_tracker.models.expense import Expense

BACKUPS_DIR = os.getenv("BACKUPS_DIR", "backups")


def backup_expenses(db: Session):
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    try:
        expenses = db.query(Expense).all()
        if not expenses:
            logging.warning("No expenses to backup")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.join(BACKUPS_DIR, f"expenses_backup_{timestamp}.csv")
        with open(file_name, "w") as f:
            f.write("id,date,description,amount\n")
            for expense in expenses:
                f.write(f"{expense.id},{expense.date},{expense.description},{expense.amount}\n")
        logging.info(f"Expenses backed up to {file_name}")
    except Exception as e:
        logging.error(f"Error backing up expenses: {e}")
