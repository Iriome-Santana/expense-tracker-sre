import os
import logging
import psycopg2


logging.basicConfig(level=logging.INFO)

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "expense_tracker"),
        user=os.getenv("DB_USER", "expense_user"),
        password=os.getenv("DB_PASSWORD", "expense_pass")
    )
    return conn

def load_expenses():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, description, amount FROM expenses")
        rows = cursor.fetchall()
        expenses = [{"id": row[0], "date": row[1], "description": row[2], "amount": row[3]} for row in rows]
        return expenses
    except psycopg2.Error as e:
        logging.error(f"Error loading expenses: {e}")
        return []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def add_expense(date, description, amount):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (date, description, amount) VALUES (%s, %s, %s)", (date, description, amount))
        conn.commit()
    except psycopg2.Error as e:
        logging.error(f"Error adding expense: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            
def delete_expense(expense_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        conn.commit()
    except psycopg2.Error as e:
        logging.error(f"Error deleting expense: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()