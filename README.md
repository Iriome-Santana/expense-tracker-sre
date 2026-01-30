# SRE Expense Tracker

Production-ready expense tracking CLI with SRE/DevOps best practices. Built to demonstrate observability, reliability, and operational excellence principles.

## Project Overview

This isn't just another expense tracker—it's a demonstration of **Site Reliability Engineering** principles applied to a simple application:

- **Observability First**: Structured logging with correlation IDs
- **Reliability**: Automated backups and data validation
- **Operability**: Environment-based configuration and error handling
- **Testability**: Comprehensive test coverage with pytest

## Features

### Core Functionality
- ✅ Add, view, and delete expenses
- ✅ Calculate expense summaries
- ✅ CSV-based persistent storage

### SRE Features
- 📊 **Structured Logging**: Every operation logged with unique run IDs
- 🔄 **Automated Backups**: Timestamped backups on startup
- ⏰ **Log Retention**: Automatic cleanup of old logs (configurable)
- 🛡️ **Input Validation**: Decorator-based validation patterns
- 🧪 **Test Coverage**: Unit tests with fixtures and mocks
- ⚙️ **12-Factor Config**: Environment variable configuration

## Prerequisites

- Python 3.8+
- pip

## Installation
```bash
# Clone the repository
git clone https://github.com/Iriome-Santana/expense-tracker-sre.git
cd expense-tracker-sre

# Install dependencies
pip install pytest

# Run the application
python cli.py
```

## Usage
```bash
# Start the application
python cli.py

# Run tests
pytest test_expenses.py -v

# Run with custom configuration
export LOG_FILE="custom.log"
export EXPENSES_FILE="my_expenses.csv"
export LOG_RETENTION_DAYS=30
python cli.py
```

## Project Structure
```
sre-expense-tracker/
├── cli.py              # Command-line interface
├── expenses.py         # Business logic and validation
├── storage.py          # Data persistence layer
├── logging_logic.py    # Logging configuration and run IDs
├── backup.py           # Backup automation
├── test_expenses.py    # Test suite
├── expenses.csv        # Data file (generated)
├── app.log            # Log file (generated)
└── backups/           # Backup directory (generated)
```

## Architecture
```
┌─────────────┐
│   CLI       │  ← User interaction
└──────┬──────┘
       │
┌──────▼──────────┐
│ ExpenseManager  │  ← Business logic + validation decorators
└──────┬──────────┘
       │
┌──────▼──────────┐
│   Storage       │  ← CSV persistence
└─────────────────┘

Crosscutting Concerns:
├── Logging (run IDs, retention)
└── Backup (automated on startup)
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
- ✅ Expense deletion with index validation
- ✅ Empty state handling
- ✅ Invalid input scenarios
- ✅ Summary calculations

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_FILE` | `app.log` | Path to log file |
| `EXPENSES_FILE` | `expenses.csv` | Path to expenses data file |
| `LOG_RETENTION_DAYS` | `7` | Days to retain log files |

## SRE Principles Demonstrated

### 1. Observability
- **Structured logging** with correlation IDs (run_id)
- **Log levels** for different severity (INFO, WARNING, ERROR)
- **Contextual information** in every log entry

### 2. Reliability
- **Automated backups** prevent data loss
- **Input validation** prevents corrupt data
- **Error handling** with graceful degradation

### 3. Operability
- **Environment-based config** for different environments
- **No hardcoded values** - externalized configuration
- **Clear error messages** for troubleshooting

### 4. Testability
- **Unit tests** with mocks to isolate components
- **Fixtures** for test setup/teardown
- **Parametrized tests** for edge cases

## Technical Highlights

### Decorator Pattern for Validation
```python
@validate_expense
def add_expense(self, date: str, description: str, amount: float):
    # Validation happens automatically via decorator
```

### Run ID Correlation
```python
# Every log entry includes a unique run ID
2026-01-30 10:15:23 - INFO - Expense added - a1b2c3d4
2026-01-30 10:15:28 - INFO - User show expenses - a1b2c3d4
```

### Automated Backup Strategy
```python
# Backup created on startup with timestamp
backups/expenses_20260130_101523.csv
```

## Learning Outcomes

This project demonstrates understanding of:

- **Python best practices**: Decorators, context managers, type hints
- **Testing patterns**: Fixtures, mocks, parametrization
- **SRE principles**: Logging, backups, config management
- **Clean architecture**: Separation of concerns, single responsibility
- **DevOps mindset**: Automation, observability, reliability

## Future Enhancements

- [ ] Dockerization with multi-stage builds
- [ ] Prometheus metrics endpoint
- [ ] CI/CD pipeline with GitHub Actions
- [ ] JSON structured logging
- [ ] Health check endpoint
- [ ] Database migration (SQLite/PostgreSQL)
- [ ] API REST with FastAPI
- [ ] Grafana dashboards

## License

MIT License - Feel free to use this project for learning!

## Author

Built by Iriome Santana as part of the journey to becoming an SRE/DevOps Engineer.

**Learning Timeline**: 2.5 weeks in the field, 1 week on this project.

---

⭐ If you find this project helpful for learning SRE principles, please star it!