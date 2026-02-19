import os
from storage import load_expenses
from datetime import datetime
import logging


os.makedirs("backups", exist_ok=True)

def backup_expenses():
    try:
        expenses = load_expenses()
        if not expenses:
            logging.warning("No expenses to backup")
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"backups/expenses_backup_{timestamp}.csv"
        with open(file_name, "w") as f:
            f.write("id,date,description,amount\n")
            for expense in expenses:
                f.write(f"{expense['id']},{expense['date']},{expense['description']},{expense['amount']}\n")
        logging.info("Expenses backed up successfully!")
    except Exception as e:
        logging.error(f"Error backing up expenses: {e}")

    