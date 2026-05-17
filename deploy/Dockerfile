FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY src/ ./src/
COPY alembic.ini .
COPY migrations/ ./migrations/

RUN pip install --upgrade pip==26.1 && \
    pip install --no-cache-dir .

CMD ["uvicorn", "expense_tracker.main:app", "--host", "0.0.0.0", "--port", "8000"]