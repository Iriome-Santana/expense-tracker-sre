import logging
import os
from datetime import datetime, timedelta

LOG_FILE = os.getenv("LOG_FILE", "app.log")
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", 7))

class RunIDFilter(logging.Filter):
    def __init__(self, run_id: str):
        super().__init__()
        self.run_id = run_id
    def filter(self, record):
        record.run_id = self.run_id
        return True
 



def setup_logging(log_file: str = LOG_FILE, run_id: str = None):
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s - %(run_id)s', 
                        handlers=handlers,
                        force=True
    )
    
    for handler in logging.getLogger().handlers:
        handler.addFilter(RunIDFilter(run_id))
    logging.info("Logger initialized")
    
    cleanup_logs()
    
def cleanup_logs():
    if not os.path.exists(LOG_FILE):
        return
    
    file_mtime = datetime.fromtimestamp(os.path.getmtime(LOG_FILE))
    if datetime.now() - file_mtime > timedelta(days=LOG_RETENTION_DAYS):
        os.remove(LOG_FILE)
        logging.info("Log file deleted")

    