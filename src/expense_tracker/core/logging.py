import logging
import os
import uuid
from datetime import datetime, timedelta
from pythonjsonlogger.json import JsonFormatter

LOG_FILE = os.getenv("LOG_FILE", "app.log")
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", 7))
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "false").lower() == "true"


class RunIDFilter(logging.Filter):
    def __init__(self, run_id: str):
        super().__init__()
        self.run_id = run_id

    def filter(self, record):
        record.run_id = self.run_id
        return True


def setup_logging(log_file: str = LOG_FILE, run_id: str = None):
    if run_id is None:
        run_id = str(uuid.uuid4())[:8]

    formatter = JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(message)s %(run_id)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "run_id": "run_id",
        },
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    handlers = [logging.StreamHandler()]

    if LOG_TO_FILE and log_file:
        handlers.append(logging.FileHandler(log_file))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.addFilter(RunIDFilter(run_id))
        root_logger.addHandler(handler)

    logging.info("Logger initialized")
    cleanup_logs()


def cleanup_logs():
    if not os.path.exists(LOG_FILE):
        return

    file_mtime = datetime.fromtimestamp(os.path.getmtime(LOG_FILE))
    if datetime.now() - file_mtime > timedelta(days=LOG_RETENTION_DAYS):
        os.remove(LOG_FILE)
        logging.info("Log file deleted")