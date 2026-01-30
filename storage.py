import os
import csv


EXPENSES_FILE = os.getenv("EXPENSES_FILE", "expenses.csv")
FIELDNAMES = ["date", "description", "amount"]

def load_expenses():
    if not os.path.exists(EXPENSES_FILE):
        return []

    try:
        with open(EXPENSES_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            expenses = list(reader)
    except OSError as e:
        logging.error(f"Error loading expenses: {e}")
        return []

    for expense in expenses:
        expense["amount"] = float(expense["amount"])
    return expenses

def save_expenses(expenses):
    try:
        with open(EXPENSES_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(expenses)
    except OSError as e:
        logging.error(f"Error saving expenses: {e}")