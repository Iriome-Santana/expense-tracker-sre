import logging
from expenses import ExpenseManager
from backup import backup_expenses
from logging_logic import *
import uuid
from errors import *

RUN_ID = str(uuid.uuid4())[:8]

def menu():
    print("\nMenu:")
    print("1. Add expense")
    print("2. Show expenses")
    print("3. Delete expense")
    print("4. Summary")
    print("5. Exit")
    option = input("Enter option: ")
    return option

def main():
    backup_expenses()
    manager = ExpenseManager()
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
                    logging.warning("User enter a invalid amount")
                    continue
                try:
                    manager.add_expense(date, description, amount)
                except NegativeAmountError:
                    print("Invalid amount")
                    logging.warning("User enter a invalid amount")
                    continue
                except FieldsRequiredError:
                    print("Fields are required")
                    logging.warning("User enter a invalid field")
                    continue
                except ValueError as e:
                    print(e)
                    logging.warning(f"User enter a invalid date: {e}")
                    continue
                print("Expense added successfully!")
                logging.info("Expense added successfully!")

            elif option == "2":
                expenses = manager.show_expenses()
                
                if not expenses:
                    print("No expenses found")
                    logging.warning("User try to show expenses but there are no expenses")
                    continue
                for index, expense in enumerate(expenses, start=1):
                    print(f"{index}. {expense['date']} - {expense['description']} - {expense['amount']}")
                logging.info("User show expenses")

            elif option == "3":
                expenses = manager.show_expenses()
                if not expenses:
                    print("No expenses to delete")
                    logging.warning("User try to delete expenses but there are no expenses")
                    continue
                for i, expense in enumerate(expenses, start=1):
                    print(f"{i}. {expense['date']} - {expense['description']} - {expense['amount']}")
                try:
                    index = int(input("Enter expense index: ")) - 1
                    expense_id= expenses[index]["id"]
                except ValueError:
                    print("Invalid index")
                    logging.warning("User enter a invalid index")
                    continue
                try:
                    manager.delete_expense(expense_id)
                    logging.info("User delete expense")
                    print("Expense deleted successfully!")
                except ValueError as e:
                    print(f"Error: {e}")
                    logging.error(f"Error deleting expense: {e}")

            elif option == "4":
                logging.info("User show summary")
                print("\nSummary:")
                print(manager.summary())

            elif option == "5":
                logging.info("User exit the program")
                print("See you later!")
                break

            else:
                print("Invalid option")
                logging.warning("User enter a inexistent option")
        except ValueError as e:
            print(e)
        
if __name__ == "__main__":
    setup_logging(LOG_FILE, RUN_ID)
    main()