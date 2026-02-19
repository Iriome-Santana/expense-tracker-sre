# SRE Expense Tracker

Production-ready expense tracking app with SRE/DevOps best practices. Built to demonstrate observability, reliability, and operational excellence principles.

## Project Overview

This isn't just another expense tracker — it's a demonstration of **Site Reliability Engineering** principles applied to a real application:

- **Observability First**: Structured logging with correlation IDs
- **Reliability**: Automated backups and data validation
- **Operability**: Environment-based configuration and error handling
- **Testability**: Comprehensive test coverage with pytest

## Features

### Core Functionality
- ✅ Add, view, and delete expenses
- ✅ Calculate expense summaries
- ✅ PostgreSQL-based persistent storage

### SRE Features
- 📊 **Structured Logging**: Every operation logged with unique run IDs
- 🔄 **Automated Backups**: Timestamped CSV exports from the database on startup
- ⏰ **Log Retention**: Automatic cleanup of old logs (configurable)
- 🛡️ **Input Validation**: Decorator-based validation patterns
- 🧪 **Test Coverage**: Unit tests with fixtures and mocks
- ⚙️ **12-Factor Config**: Environment variable configuration
- 🌐 **REST API**: FastAPI endpoints for all core operations

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip

## Installation

```bash
# Clone the repository
git clone https://github.com/Iriome-Santana/expense-tracker-sre.git
cd expense-tracker-sre

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install psycopg2-binary fastapi uvicorn pytest
```

## Database Setup

```bash
# Start PostgreSQL
sudo service postgresql start

# Create user and database
sudo -u postgres psql

CREATE USER expense_user WITH PASSWORD 'expense_pass';
CREATE DATABASE expense_tracker OWNER expense_user;
GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO expense_user;
\q

# Create the expenses table
sudo -u postgres psql -d expense_tracker

CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL
);
ALTER TABLE expenses OWNER TO expense_user;
\q
```

## Usage

### CLI
```bash
# Start the application
python cli.py

# Run with custom configuration
export DB_HOST="localhost"
export DB_NAME="expense_tracker"
export DB_USER="expense_user"
export DB_PASSWORD="expense_pass"
export LOG_FILE="custom.log"
export LOG_RETENTION_DAYS=30
python cli.py
```

### API
```bash
# Start the API server
uvicorn main:app --reload

# API available at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/expenses` | List all expenses |
| POST | `/expenses` | Add a new expense |
| DELETE | `/expenses/{id}` | Delete an expense by ID |
| GET | `/expenses/summary` | Get total amount |

### Example request
```json
POST /expenses
{
  "date": "2026-02-19",
  "description": "Coffee",
  "amount": 3.50
}
```

## Project Structure

```
expense-tracker-sre/
├── main.py             # FastAPI application and endpoints
├── cli.py              # Command-line interface
├── expenses.py         # Business logic and validation
├── storage.py          # PostgreSQL persistence layer
├── logging_logic.py    # Logging configuration and run IDs
├── backup.py           # Backup automation (exports DB to CSV)
├── errors.py           # Custom exceptions
├── test_expenses.py    # Test suite
├── app.log             # Log file (generated)
└── backups/            # Backup directory (generated)
```

## Architecture

```
┌─────────────┐    ┌─────────────┐
│   CLI       │    │  FastAPI    │  ← Interfaces
└──────┬──────┘    └──────┬──────┘
       │                  │
       └────────┬──────────┘
                │
┌───────────────▼─────────────────┐
│         ExpenseManager          │  ← Business logic + validation
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│           storage.py            │  ← PostgreSQL persistence
└───────────────┬─────────────────┘
                │
┌───────────────▼─────────────────┐
│          PostgreSQL             │  ← Database
└─────────────────────────────────┘

Crosscutting Concerns:
├── Logging (run IDs, retention)
└── Backup (CSV export on startup)
```

## Testing

```bash
# Run all tests
pytest test_expenses.py -v

# Run with coverage report
pip install pytest-cov
pytest test_expenses.py --cov=expenses --cov-report=term-missing
```

### Test Coverage
- ✅ Expense addition with validation
- ✅ Negative and zero amount handling
- ✅ Empty fields handling
- ✅ Expense deletion
- ✅ Empty state handling
- ✅ Summary calculations

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_NAME` | `expense_tracker` | Database name |
| `DB_USER` | `expense_user` | Database user |
| `DB_PASSWORD` | `expense_pass` | Database password |
| `LOG_FILE` | `app.log` | Path to log file |
| `LOG_RETENTION_DAYS` | `7` | Days to retain log files |

## SRE Principles Demonstrated

### 1. Observability
- **Structured logging** with correlation IDs (run_id)
- **Log levels** for different severity (INFO, WARNING, ERROR)
- **Contextual information** in every log entry

### 2. Reliability
- **Automated backups** on startup — exports DB to timestamped CSV
- **Input validation** prevents corrupt data (date format, negative amounts)
- **Error handling** with graceful degradation

### 3. Operability
- **Environment-based config** for different environments
- **No hardcoded values** — externalized configuration
- **Clear error messages** for troubleshooting
- **REST API** for programmatic access

### 4. Testability
- **Unit tests** with mocks to isolate components
- **Fixtures** for test setup/teardown
- **In-memory fake DB** in tests — no real database needed

## Roadmap

- [ ] Dockerization with Docker Compose
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Cloud deployment
- [ ] Prometheus metrics endpoint
- [ ] JSON structured logging
- [ ] Grafana dashboards

## Author

Built by Iriome Santana as part of the journey to becoming an SRE/DevOps Engineer.

---

⭐ If you find this project helpful for learning SRE principles, please star it!