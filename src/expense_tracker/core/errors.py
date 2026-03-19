from fastapi import HTTPException

class AppError(HTTPException):
    """Base para todos los errores de la aplicación."""
    pass


class NegativeAmountError(AppError):
    def __init__(self):
        super().__init__(status_code=400, detail="Amount must be greater than 0")


class FieldsRequiredError(AppError):
    def __init__(self):
        super().__init__(status_code=400, detail="All fields are required")

class ExpenseNotFoundError(AppError):
    def __init__(self, expense_id: int):
        super().__init__(status_code=404, detail=f"Expense with id {expense_id} not found")