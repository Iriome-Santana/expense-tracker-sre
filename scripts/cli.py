import logging
import uuid

from expense_tracker.services.expense_service import ExpenseService
from expense_tracker.services.backup_service import backup_expenses
from expense_tracker.core.logging import setup_logging, LOG_FILE
from expense_tracker.core.errors import NegativeAmountError, FieldsRequiredError
from expense_tracker.db.session import SessionLocal

RUN_ID = str(uuid.uuid4())[:8]


def menu():
    print("\nMenu:")
    print("1. Add expense")
    print("2. Show expenses")
    print("3. Delete expense")
    print("4. Summary")
    print("5. Exit")
    return input("Enter option: ")


def main():
    db = SessionLocal()
    try:
        backup_expenses(db)
        manager = ExpenseService()
        while True:
            option = menu()
            try:
                if option == "1":
                    date = input("Enter date (YYYY-MM-DD): ")
                    description = input("Enter description: ")
                    try:
                        amount = float(input("Enter amount: "))
                    except ValueError:
                        print("Amount must be a number")
                        logging.warning("User entered an invalid amount")
                        continue
                    try:
                        manager.add_expense(db, date, description, amount)
                    except NegativeAmountError:
                        print("Invalid amount")
                        logging.warning("User entered a negative amount")
                        continue
                    except FieldsRequiredError:
                        print("Fields are required")
                        logging.warning("User left a required field empty")
                        continue
                    except ValueError as e:
                        print(e)
                        logging.warning(f"User entered an invalid date: {e}")
                        continue
                    print("Expense added successfully!")
                    logging.info("Expense added successfully!")

                elif option == "2":
                    expenses = manager.show_expenses(db)
                    if not expenses:
                        print("No expenses found")
                        logging.warning("No expenses to show")
                        continue
                    for index, expense in enumerate(expenses, start=1):
                        print(f"{index}. {expense.date} - {expense.description} - {expense.amount}")
                    logging.info("User viewed expenses")

                elif option == "3":
                    expenses = manager.show_expenses(db)
                    if not expenses:
                        print("No expenses to delete")
                        logging.warning("No expenses to delete")
                        continue
                    for i, expense in enumerate(expenses, start=1):
                        print(f"{i}. {expense.date} - {expense.description} - {expense.amount}")
                    try:
                        index = int(input("Enter expense index: ")) - 1
                        expense_id = expenses[index].id
                    except (ValueError, IndexError):
                        print("Invalid index")
                        logging.warning("User entered an invalid index")
                        continue
                    try:
                        manager.delete_expense(db, expense_id)
                        logging.info("Expense deleted")
                        print("Expense deleted successfully!")
                    except ValueError as e:
                        print(f"Error: {e}")
                        logging.error(f"Error deleting expense: {e}")

                elif option == "4":
                    logging.info("User viewed summary")
                    print("\nSummary:")
                    print(manager.summary(db))

                elif option == "5":
                    logging.info("User exited")
                    print("See you later!")
                    break

                else:
                    print("Invalid option")
                    logging.warning("User entered an invalid option")

            except ValueError as e:
                print(e)
    finally:
        db.close()


if __name__ == "__main__":
    setup_logging(LOG_FILE, RUN_ID)
    main()