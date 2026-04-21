import os
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from expense_tracker.models.expense import Expense

BACKUPS_DIR = os.getenv("BACKUPS_DIR", "backups")
S3_BACKUP_BUCKET = os.getenv("S3_BACKUP_BUCKET", "")


def _generate_csv_content(expenses) -> str:
    """Genera el contenido CSV como string."""
    lines = ["id,date,description,amount"]
    for expense in expenses:
        lines.append(f"{expense.id},{expense.date},{expense.description},{expense.amount}")
    return "\n".join(lines)


def _backup_to_s3(csv_content: str, filename: str) -> None:
    """Sube el backup a S3."""
    import boto3
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=S3_BACKUP_BUCKET,
        Key=f"backups/{filename}",
        Body=csv_content.encode("utf-8"),
        ContentType="text/csv",
    )
    logging.info(f"Backup uploaded to s3://{S3_BACKUP_BUCKET}/backups/{filename}")


def _backup_to_disk(csv_content: str, filename: str) -> None:
    """Guarda el backup en disco local."""
    os.makedirs(BACKUPS_DIR, exist_ok=True)
    filepath = os.path.join(BACKUPS_DIR, filename)
    with open(filepath, "w") as f:
        f.write(csv_content)
    logging.info(f"Backup saved to {filepath}")


def backup_expenses(db: Session) -> None:
    """
    Exporta todos los gastos a CSV.
    Si S3_BACKUP_BUCKET está definida → sube a S3.
    Si no → guarda en disco local.
    """
    try:
        expenses = db.query(Expense).all()
        if not expenses:
            logging.warning("No expenses to backup")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"expenses_backup_{timestamp}.csv"
        csv_content = _generate_csv_content(expenses)

        if S3_BACKUP_BUCKET:
            _backup_to_s3(csv_content, filename)
        else:
            _backup_to_disk(csv_content, filename)

    except Exception as e:
        logging.error(f"Error backing up expenses: {e}")