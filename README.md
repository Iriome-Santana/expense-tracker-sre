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
- 🐳 **Dockerized**: Full containerization with Docker Compose
- 🔁 **CI Pipeline**: Automated testing with GitHub Actions

## Prerequisites

### Running locally
- Python 3.8+
- PostgreSQL
- pip

### Running with Docker
- Docker
- Docker Compose

## Installation

### Option 1 — Local

```bash
# Clone the repository
git clone https://github.com/Iriome-Santana/expense-tracker-sre.git
cd expense-tracker-sre

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2 — Docker (recommended)

```bash
git clone https://github.com/Iriome-Santana/expense-tracker-sre.git
cd expense-tracker-sre
docker-compose up
```

That's it. The API and database are ready at `http://localhost:8002`.

## Database Setup (local only)

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
python cli.py
```

### API
```bash
# Local
uvicorn main:app --reload

# Docker
docker-compose up
```

API available at `http://localhost:8000` (local) or `http://localhost:8002` (Docker).
Interactive docs at `/docs`.

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
├── .github/
│   └── workflows/
│       └── ci.yml          # GitHub Actions CI pipeline
├── main.py                 # FastAPI application and endpoints
├── cli.py                  # Command-line interface
├── expenses.py             # Business logic and validation
├── storage.py              # PostgreSQL persistence layer
├── logging_logic.py        # Logging configuration and run IDs
├── backup.py               # Backup automation (exports DB to CSV)
├── errors.py               # Custom exceptions
├── test_expenses.py        # Test suite
├── Dockerfile              # Container definition for the API
├── docker-compose.yml      # Multi-container orchestration
├── init.sql                # Database initialization script
├── requirements.txt        # Python dependencies
├── app.log                 # Log file (generated)
└── backups/                # Backup directory (generated)
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

## Architecture Decisions

### Why PostgreSQL instead of CSV?
The original version used a CSV file for persistence. This worked for a prototype but had real limitations: no concurrent access, full file rewrite on every change, no data types, no queries. PostgreSQL solves all of this. It also reflects how production systems actually work — and makes the app ready for containerization, since the database lives in its own service.

### Why separate storage.py from expenses.py?
The storage layer is completely isolated from the business logic. `expenses.py` doesn't know if data comes from PostgreSQL, a CSV, or an in-memory list — it just calls `load_expenses()`, `add_expense()`, and `delete_expense()`. This separation made it possible to migrate from CSV to PostgreSQL without touching the business logic or the tests, which is a core principle of clean architecture.

### Why Docker Compose instead of a single container?
The app has two independent components — the API and the database. Running them in separate containers follows the single responsibility principle and reflects how real microservice environments work. Docker Compose handles the networking between them automatically and allows each service to be scaled or replaced independently.

### Why init.sql instead of migrations?
For a project at this stage, a simple `init.sql` is enough — it runs automatically when the PostgreSQL container starts for the first time. A migration tool like Alembic would be the next step as the schema evolves.

### Why mock the database in tests instead of using a real one?
Tests should be fast, isolated, and not depend on external infrastructure. By using an in-memory `fake_db` in the test fixture, the tests run in milliseconds and work anywhere — including in the CI pipeline on GitHub Actions — without needing a real PostgreSQL instance.

### Why validate dates in Python before hitting the database?
PostgreSQL would catch invalid dates too, but the error it returns is a low-level database exception that's hard to handle cleanly. Validating in the `validate_expense` decorator means the error is caught early, translated into a meaningful message, and never reaches the database. This is the "fail fast" principle.

## Testing

```bash
# Run all tests
pytest test_expenses.py -v

# Run with coverage report
pytest test_expenses.py --cov=expenses --cov-report=term-missing
```

### Test Coverage
- ✅ Expense addition with validation
- ✅ Negative and zero amount handling
- ✅ Empty fields handling
- ✅ Expense deletion
- ✅ Empty state handling
- ✅ Summary calculations

## CI Pipeline

Every push and pull request to `main` triggers the CI pipeline automatically via GitHub Actions:

1. Checkout code
2. Set up Python 3.12
3. Install dependencies
4. Run tests with coverage

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
- **One-command deployment** with Docker Compose

### 4. Testability
- **Unit tests** with mocks to isolate components
- **Fixtures** for test setup/teardown
- **In-memory fake DB** in tests — no real database needed
- **Automated CI** runs tests on every push

## Roadmap

- [x] PostgreSQL persistence
- [x] REST API with FastAPI
- [x] Dockerization with Docker Compose
- [x] CI pipeline with GitHub Actions
- [ ] Cloud deployment
- [ ] Prometheus metrics endpoint
- [ ] JSON structured logging
- [ ] Grafana dashboards

## Author

Built by Iriome Santana as part of the journey to becoming an SRE/DevOps Engineer.

---

⭐ If you find this project helpful for learning SRE principles, please star it!