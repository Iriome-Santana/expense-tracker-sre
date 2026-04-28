# 💸 SRE Expense Tracker

> A production-ready expense tracking REST API built to demonstrate **Site Reliability Engineering** and **DevOps** principles — not just a CRUD app.

[![CI](https://github.com/Iriome-Santana/expense-tracker-sre/actions/workflows/ci.yml/badge.svg)](https://github.com/Iriome-Santana/expense-tracker-sre/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![AWS](https://img.shields.io/badge/AWS-EC2%20%2B%20S3-FF9900?logo=amazonaws)
![License](https://img.shields.io/badge/license-MIT-lightgrey)
[![Docker Hub](https://img.shields.io/docker/pulls/iriome2512/expense-tracker?logo=docker)](https://hub.docker.com/r/iriome2512/expense-tracker)

---

## Table of Contents

- [What is this?](#-what-is-this)
- [Architecture](#-architecture)
- [Cloud Deployment](#-cloud-deployment-aws)
- [Project Structure](#-project-structure)
- [SRE Principles in Practice](#-sre-principles-in-practice)
- [Tech Stack](#-tech-stack)
- [Monitoring Dashboards](#-monitoring-dashboards)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Environment Variables](#-environment-variables)
- [Running Tests](#-running-tests)
- [Architecture Decision Records](#-architecture-decision-records)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## What is this?

This project started as a simple expense tracker and evolved into a **learning ground for SRE/DevOps engineering**. Every technical decision — from folder structure to error handling — was made deliberately and is documented here.

The goal is not just to build something that works, but to build something that is **observable, reliable, operable, and testable** — the four pillars of Site Reliability Engineering.

This is a self-taught project. If you're also learning SRE/DevOps, feel free to explore, fork, and open issues with feedback. I'd love to hear from other engineers on the same path.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          INTERFACES                             │
│                                                                 │
│   ┌─────────────────┐           ┌─────────────────────────┐    │
│   │   CLI (scripts) │           │   FastAPI REST API       │    │
│   │   cli.py        │           │   /expenses  /summary   │    │
│   └────────┬────────┘           └────────────┬────────────┘    │
│            │                                 │                  │
└────────────┼─────────────────────────────────┼──────────────────┘
             │                                 │
             └──────────────┬──────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                      BUSINESS LOGIC                              │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │                   ExpenseService                         │   │
│   │   + @validate_expense decorator (fail fast principle)    │   │
│   │   add_expense()  show_expenses()  delete_expense()       │   │
│   │   summary()                                              │   │
│   └──────────────────────────────┬───────────────────────────┘   │
│                                  │                               │
└──────────────────────────────────┼───────────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────────┐
│                      PERSISTENCE LAYER                           │
│                                                                  │
│   ┌──────────────────────────────────────────────────────────┐   │
│   │         SQLAlchemy ORM  ·  session.py                    │   │
│   │         get_db() → yields session → closes in finally    │   │
│   └──────────────────────────────┬───────────────────────────┘   │
│                                  │                               │
└──────────────────────────────────┼───────────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────────┐
│                          DATABASE                                │
│                                                                  │
│                     PostgreSQL 15                                │
│              (Docker service · persistent volume)                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

Cross-cutting concerns
├── Structured logging with unique run_id per session (core/logging.py)
├── Automated CSV backups on every write → S3  (services/backup_service.py)
├── HTTP-aware custom exceptions               (core/errors.py)
└── Generic error handler — no tracebacks in production (main.py)
```

### Docker Compose topology (local)

```
┌─────────────────────────────────────────┐
│            Docker Network               │
│                                         │
│  ┌───────────────┐  ┌────────────────┐  │
│  │   api         │  │   db           │  │
│  │   :8002→8000  │──│   postgres:15  │  │
│  │               │  │   :5432        │  │
│  └───────────────┘  └───────┬────────┘  │
│                             │           │
│                    postgres_data volume │
└─────────────────────────────────────────┘

api depends_on db (condition: service_healthy)
db healthcheck: pg_isready every 5s
```

---

## ☁️ Cloud Deployment (AWS)

The application is deployed on AWS using a **rehosting strategy** (lift-and-shift) as the first milestone of a progressive cloud adoption roadmap.

### Live infrastructure

```
┌─────────────────────────────────────────────────────┐
│                    AWS Cloud (eu-west-1)             │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │         EC2 t3.micro · Elastic IP            │   │
│  │                                              │   │
│  │  ┌──────────────────────────────────────┐   │   │
│  │  │         Docker Compose               │   │   │
│  │  │  ┌─────────────┐ ┌────────────────┐  │   │   │
│  │  │  │  api        │ │  db            │  │   │   │
│  │  │  │  FastAPI    │─│  PostgreSQL 15 │  │   │   │
│  │  │  │  :8000      │ │  :5432        │  │   │   │
│  │  │  └──────┬──────┘ └────────────────┘  │   │   │
│  │  └─────────┼────────────────────────────┘   │   │
│  └────────────┼─────────────────────────────────┘   │
│               │ boto3 · s3.put_object()              │
│               ▼                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │   S3 Bucket                                 │   │
│  │   expense-tracker-backups-iriome-2026        │   │
│  │   ├── Versioning enabled                    │   │
│  │   └── Lifecycle policy:                     │   │
│  │       30d → Standard-IA                     │   │
│  │       90d → Glacier                         │   │
│  │       365d → Delete                         │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### IAM security model

```
EC2 Instance Profile → ec2-s3-readonly-role
├── expense-tracker-s3-backup-policy (custom, least privilege)
│   ├── s3:PutObject   → expense-tracker-backups-iriome-2026/*
│   ├── s3:GetObject   → expense-tracker-backups-iriome-2026/*
│   └── s3:ListBucket  → expense-tracker-backups-iriome-2026
└── AmazonSSMManagedInstanceCore (AWS managed)
    └── allows SSM Agent to receive commands from Systems Manager
        no inbound ports required
```

No credentials are stored on the instance. The API authenticates to S3 using the IAM Instance Profile — boto3 picks up the temporary credentials automatically. Deployment commands are sent via SSM — no SSH port needs to be open.

### CI/CD pipeline

```
Push to main
    │
    ▼
GitHub Actions: run tests (pytest)
    │
    ▼
GitHub Actions: build image → push to Docker Hub
    │
    ▼
GitHub Actions: AWS CLI → SSM send-command → EC2
                          docker compose pull
                          docker compose up -d
                          docker image prune -f
```

No SSH involved. GitHub Actions authenticates to AWS via IAM credentials and sends commands to the EC2 instance through SSM Session Manager. Port 22 is not open to the internet.

### Deployment strategy: Rehosting (intentional)

This deployment is a deliberate **rehosting** (lift-and-shift) of the existing Docker Compose stack onto EC2. The application runs identically to the local environment, with one key difference: CSV backups are written directly to S3 instead of the local filesystem.

This was a conscious architectural decision. See [Why EC2 + S3 instead of RDS?](#why-ec2--s3-instead-of-rds) in the ADR section.

The next milestone is **replatforming**: migrating the API to ECS Fargate with RDS PostgreSQL, Terraform-managed infrastructure, and a full CI/CD deployment pipeline.

```
v1 ✅ Rehosting   — EC2 + Docker Compose + S3 backups + SSM CD (current)
v2 ⏳ Monitoring  — CloudWatch Agent + Prometheus + Grafana
v3 ⏳ Replatform  — ECS Fargate + RDS + Terraform + full CI/CD
```

### How the backup pipeline works

```
POST /expenses/ or DELETE /expenses/{id}
          │
          ▼
ExpenseService writes to PostgreSQL
          │
          ▼
backup_expenses(db) is called
          │
          ├── S3_BACKUP_BUCKET defined? ──Yes──▶ boto3 s3.put_object()
          │                                       s3://bucket/backups/
          │                                       expenses_backup_TIMESTAMP.csv
          └── No ──▶ write to local disk
                     (development mode)
```

Backups are triggered on every write operation, not on a schedule. If the EC2 instance is replaced or terminated, all backups survive independently in S3.

### How to deploy manually

The EC2 instance is bootstrapped via a User Data script that runs once on first launch:

1. Installs Docker and Docker Compose
2. Downloads `docker-compose.prod.yml` from this repository
3. Creates `/app/.env` with production environment variables
4. Pulls the latest image from Docker Hub and starts the stack

To update the application manually without going through the CI/CD pipeline:

```bash
# Send command to EC2 via SSM (no SSH required)
aws ssm send-command \
  --instance-ids <INSTANCE_ID> \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["cd /app && docker compose pull && docker compose --env-file /app/.env up -d"]' \
  --region eu-west-1
```

Every push to `main` triggers the full pipeline automatically — tests, build, and deploy.

---

## 📁 Project Structure

```
expense-tracker/
├── src/
│   └── expense_tracker/           # Main package (src-layout)
│       ├── main.py                # FastAPI app · lifespan · error handlers
│       ├── models/
│       │   └── expense.py         # SQLAlchemy ORM model (Expense table)
│       ├── schemas/
│       │   └── expense.py         # Pydantic I/O schemas
│       ├── services/
│       │   ├── expense_service.py # Business logic + @validate_expense
│       │   └── backup_service.py  # CSV export → S3 or local disk
│       ├── api/
│       │   └── routes/
│       │       └── expenses.py    # HTTP endpoints (GET/POST/DELETE)
│       ├── db/
│       │   └── session.py         # Engine · SessionLocal · get_db()
│       └── core/
│           ├── errors.py          # HTTP-aware custom exceptions
│           └── logging.py         # run_id filter · log retention
├── scripts/
│   └── cli.py                     # Interactive CLI (uses same service layer)
├── tests/
│   ├── conftest.py                # pytest fixtures (mock db + service)
│   └── test_expenses.py           # 11 unit tests — no real DB needed
├── deploy/
│   ├── Dockerfile                 # python:3.12-slim · pip install .
│   ├── docker-compose.yml         # local: api + db + prometheus + grafana
│   └── docker-compose.prod.yml    # production: api + db only
├── .github/
│   └── workflows/
│       └── ci.yml                 # test → build → push → deploy via SSM
├── pyproject.toml                 # Dependencies · pytest config · build
├── .env.example                   # Environment variable template
└── .gitignore
```

---

## SRE Principles in Practice

### 1. Observability

Every CLI session generates a unique `run_id` that is injected into every log line:

```
2026-03-18 14:30:22 - INFO  - Expense added successfully! - a3f9b2c1
2026-03-18 14:30:25 - INFO  - User viewed expenses        - a3f9b2c1
2026-03-18 14:31:01 - INFO  - User exited                 - a3f9b2c1
```

This means you can `grep a3f9b2c1 app.log` and reconstruct exactly what happened in one session — a core observability pattern used in distributed systems with trace IDs.

Log retention is also automated: logs older than `LOG_RETENTION_DAYS` are deleted on startup.

### 2. Reliability — Fail Fast

Input validation happens at the decorator level, before touching the database:

```python
@validate_expense
def add_expense(self, db, date, description, amount):
    # data is guaranteed valid here
```

The `@validate_expense` decorator catches invalid dates, empty fields, and negative amounts early, returning a clean HTTP 400 to the client instead of propagating errors down to the database layer.

Custom exceptions carry their own HTTP status codes:

```python
class NegativeAmountError(AppError):
    def __init__(self):
        super().__init__(status_code=400, detail="Amount must be greater than 0")

class ExpenseNotFoundError(AppError):
    def __init__(self, expense_id: int):
        super().__init__(status_code=404, detail=f"Expense with id {expense_id} not found")
```

### 3. Reliability — Automated Backups to S3

On every write operation (POST or DELETE), all expenses are exported to a timestamped CSV and uploaded directly to S3:

```
s3://expense-tracker-backups-iriome-2026/backups/
├── expenses_backup_20260422_221044.csv
├── expenses_backup_20260422_222208.csv
└── expenses_backup_20260422_222235.csv
```

The backup destination is controlled by the `S3_BACKUP_BUCKET` environment variable:

- **Defined** → uploads to S3 using the EC2 IAM Instance Profile (no credentials in code)
- **Not defined** → writes to local disk (development mode, backward compatible)

### 4. Operability

- All configuration via environment variables — no hardcoded values
- One-command deployment with Docker Compose
- `service_healthy` condition on `depends_on` — the API never starts before PostgreSQL is ready
- `restart: always` in production Compose — containers recover automatically from crashes
- Generic error handler in production — no tracebacks exposed to clients
- Interactive API docs at `/docs` — no external tooling needed to explore the API
- Deployment via SSM Session Manager — no SSH port open to the internet

### 5. Testability

- 11 unit tests, all passing
- Database is fully mocked with `MagicMock` — tests run in ~0.02s with no PostgreSQL instance
- CI pipeline runs the full suite on every push and pull request to `main`
- `pytest-cov` for coverage reporting

---

## Monitoring Dashboards

The application exposes a `/metrics` endpoint that Prometheus scrapes every 15 seconds. Grafana visualizes the data in real time.

![Grafana Dashboards](docs/images/dashboards.png)

**Dashboards included:**
- **HTTP Requests Total** — accumulated request count per endpoint (`sum by (handler)`)
- **Request Rate by Endpoint** — real-time requests/sec per endpoint (`sum by (handler) (rate(...))`)
- **Total Expenses Created** — stat panel showing the running counter
- **Expenses in Database** — gauge with color thresholds (green → orange at 50 → red at 80)

> Prometheus and Grafana are included in the local `docker-compose.yml` but excluded from the production stack (`docker-compose.prod.yml`) to stay within the 1GB RAM limit of a t3.micro. Adding observability to the production environment is the next planned milestone.

---

## 🛠 Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| API framework | FastAPI 0.129 | Automatic OpenAPI docs, async-ready, Pydantic v2 |
| ORM | SQLAlchemy 2.0 | Clean separation between models and queries |
| Validation | Pydantic v2 | Type-safe request/response schemas |
| Database | PostgreSQL 15 | Production-grade, concurrent, typed |
| Testing | pytest + pytest-cov | Fast, fixture-based, coverage reporting |
| Containerization | Docker Compose | Two-service orchestration (api + db) |
| CI/CD | GitHub Actions | Test → build → push → deploy on every push to main |
| Package mgmt | pyproject.toml | Modern Python standard (PEP 517/518) |
| Cloud compute | AWS EC2 t3.micro | Low cost, full Docker support, Elastic IP for stable endpoint |
| Cloud storage | AWS S3 | Durable backup storage, decoupled from instance lifecycle |
| Remote access | AWS SSM Session Manager | Zero open admin ports — deployment without SSH |

---

## Quick Start

### Option 1 — Docker (recommended)

```bash
git clone https://github.com/Iriome-Santana/expense-tracker-sre.git
cd expense-tracker-sre

# Copy and configure environment variables
cp .env.example .env
nano .env  # Set your values (see Environment Variables section)

# Start both services
docker compose --env-file .env -f deploy/docker-compose.yml up --build
```

API available at **http://localhost:8002**
Interactive docs at **http://localhost:8002/docs**

Or pull the pre-built image directly from Docker Hub:

```bash
docker pull iriome2512/expense-tracker
```

### Option 2 — Local

**Prerequisites:** Python 3.12+, PostgreSQL running locally.

```bash
git clone https://github.com/Iriome-Santana/expense-tracker-sre.git
cd expense-tracker-sre

# Install package + dev dependencies
pip install -e ".[dev]"

# Set environment variables
export DB_HOST=localhost
export DB_NAME=expense_tracker
export DB_USER=expense_user
export DB_PASSWORD=expense_pass

# Start the API
uvicorn expense_tracker.main:app --reload
```

API available at **http://localhost:8000**

### Option 3 — CLI

```bash
pip install -e ".[dev]"
python scripts/cli.py
```

> The CLI requires a running PostgreSQL instance (Docker or local).

---

## API Reference

| Method | Endpoint | Description | Success | Error |
|--------|----------|-------------|---------|-------|
| `GET` | `/` | Health check | 200 | — |
| `GET` | `/expenses/summary` | Total amount | 200 | — |
| `GET` | `/expenses/` | List all expenses | 200 | — |
| `POST` | `/expenses/` | Create expense | 201 | 400 |
| `DELETE` | `/expenses/{id}` | Delete by ID | 200 | 404 |

### Create expense

```bash
curl -X POST http://localhost:8002/expenses/ \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-03-18", "description": "Coffee", "amount": 3.50}'

# 201 Created
{"message": "Expense added successfully!"}
```

### Validation error

```bash
curl -X POST http://localhost:8002/expenses/ \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-03-18", "description": "Coffee", "amount": -5}'

# 400 Bad Request
{"detail": "Amount must be greater than 0"}
```

### Not found

```bash
curl -X DELETE http://localhost:8002/expenses/999

# 404 Not Found
{"detail": "Expense with id 999 not found"}
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host (`db` inside Docker) |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `expense_tracker` | Database name |
| `DB_USER` | `expense_user` | Database user |
| `DB_PASSWORD` | `expense_pass` | Database password |
| `POSTGRES_USER` | — | Used by the PostgreSQL Docker image |
| `POSTGRES_PASSWORD` | — | Used by the PostgreSQL Docker image |
| `POSTGRES_DB` | — | Used by the PostgreSQL Docker image |
| `LOG_FILE` | `app.log` | Log file path |
| `LOG_RETENTION_DAYS` | `7` | Days before log file is deleted |
| `BACKUPS_DIR` | `backups` | Directory for local CSV backups (development) |
| `S3_BACKUP_BUCKET` | `` | S3 bucket name for backups. If empty, falls back to local disk |

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore` by default.

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=expense_tracker --cov-report=term-missing

# Run without installing the package
PYTHONPATH=src python -m pytest tests/ -v
```

```
collected 11 items

tests/test_expenses.py::test_add_expense                 PASSED
tests/test_expenses.py::test_add_expense_amount_negative PASSED
tests/test_expenses.py::test_add_expense_amount_zero     PASSED
tests/test_expenses.py::test_add_expense_empty_fields    PASSED
tests/test_expenses.py::test_add_expense_invalid_date    PASSED
tests/test_expenses.py::test_show_expenses               PASSED
tests/test_expenses.py::test_show_expenses_empty         PASSED
tests/test_expenses.py::test_delete_expense              PASSED
tests/test_expenses.py::test_delete_expense_not_found    PASSED
tests/test_expenses.py::test_summary                     PASSED
tests/test_expenses.py::test_summary_empty               PASSED

11 passed in 0.02s
```

Tests use `MagicMock` for the database session — **no PostgreSQL instance required**.

---

## Architecture Decision Records

### Why src-layout instead of flat structure?

The original version had all files in the root directory. This works for scripts but breaks for installable packages: Python can accidentally import from the working directory instead of the installed package, causing subtle bugs that only appear in production. The `src/` layout forces Python to always import from the installed package, making the project behave identically locally and inside Docker.

### Why SQLAlchemy ORM instead of raw SQL?

Raw SQL is fine for simple queries, but as the schema grows, managing connections, transactions, and query composition becomes error-prone. SQLAlchemy provides a clean session lifecycle (`get_db()` with `finally: db.close()`), type-safe models, and `pool_pre_ping=True` which silently reconnects dropped database connections — important for long-running Docker services.

### Why pyproject.toml instead of requirements.txt?

`requirements.txt` only lists dependencies. `pyproject.toml` (PEP 517/518) defines the entire build system: dependencies, dev dependencies, pytest config, coverage config, and package discovery — all in one file. It also makes the project installable with `pip install -e .`, which is how both local development and the Dockerfile work consistently.

### Why mock the database in tests instead of a test database?

Tests should be **fast, isolated, and infrastructure-free**. A real PostgreSQL instance adds startup time, requires configuration in CI, and can produce flaky results if state leaks between tests. `MagicMock` lets us test all business logic in ~0.02s with no external dependencies — tests run identically on any machine and in GitHub Actions.

### Why HTTPException subclasses instead of separate exception handlers?

FastAPI already knows how to handle `HTTPException` — it reads `status_code` and `detail` and builds a clean JSON response automatically. By making custom exceptions subclass it, each error carries its own HTTP semantics (`400`, `404`) without needing to register a separate `@app.exception_handler` for every type. One `AppError` base class, and FastAPI handles the rest.

### Why `depends_on: condition: service_healthy` instead of just `depends_on`?

The basic `depends_on` only waits for the container process to start, not for PostgreSQL to be ready to accept connections. PostgreSQL takes 1–3 seconds to initialize after the container starts. Without a healthcheck, the API starts, tries to connect, fails, and crashes. The `pg_isready` healthcheck polls every 5 seconds and only marks the service healthy when PostgreSQL is genuinely accepting connections.

### Why EC2 + S3 instead of RDS?

RDS PostgreSQL adds ~$15–18/month for a managed service whose main benefits are automated backups, point-in-time recovery, and failover. For this project, the backup requirement is already covered by `backup_service.py` writing timestamped CSVs directly to S3 on every write operation, and the traffic profile doesn't justify multi-AZ failover.

Running PostgreSQL in a container on the same EC2 host eliminates network latency between the API and the database, reduces costs by ~65%, and keeps the deployment identical to the local Docker Compose environment — reducing the surface area for environment-specific bugs.

S3 is kept as a separate service deliberately: it decouples backup storage from the EC2 instance lifecycle. If the instance is terminated or replaced, all backups survive independently.

This decision would be revisited if the project required concurrent writes from multiple instances, point-in-time recovery, or a read replica.

### Why rehosting instead of replatforming from the start?

Rehosting (lift-and-shift) was chosen deliberately as the first cloud milestone for two reasons. First, it validates that the containerised stack runs correctly in AWS with minimal risk — if something breaks, the diff from local is small. Second, it preserves AWS credits: a t3.micro running Docker Compose costs a fraction of an ECS Fargate + RDS setup, extending the available runway for learning without financial pressure.

The architecture is documented as intentional rehosting, not as the final state. Replatforming to ECS + RDS + Terraform is the next planned milestone, once the application behaviour in AWS is fully understood.

### Why SSM Session Manager instead of SSH for deployment?

The initial CD implementation used `appleboy/ssh-action` to deploy via SSH. This required port 22 to be open to `0.0.0.0/0` because GitHub Actions uses unpredictable IP ranges that cannot be whitelisted statically.

SSM Session Manager eliminates the need for an open SSH port entirely. The EC2 instance connects outbound to the SSM service and maintains a persistent channel. GitHub Actions sends deployment commands through the AWS API using IAM credentials — no inbound port is involved. This reduces the attack surface to zero for the deployment path while keeping the same operational capability.

The tradeoff is added IAM complexity: the EC2 role needs `AmazonSSMManagedInstanceCore` and GitHub Actions needs AWS credentials with SSM permissions. For a security improvement of this magnitude, the complexity is justified.

### Security tradeoff: credentials in User Data

Database credentials are currently stored in a `.env` file on the EC2 instance, created during bootstrap via User Data. This is acceptable for a single-instance personal project but would be replaced with AWS Secrets Manager in a multi-person or production environment.

The IAM policy for S3 access follows least-privilege: the instance profile only grants `PutObject`, `GetObject`, and `ListBucket` on the specific backup bucket — not `AmazonS3FullAccess` or any account-wide permission.

### Why Prometheus and Grafana are excluded from the production stack?

A t3.micro has 1GB of RAM. Running api + db + prometheus + grafana simultaneously pushes the instance into swap, which degrades performance unpredictably. The production `docker-compose.prod.yml` runs only the two essential services (~600MB combined), leaving headroom for OS processes and traffic spikes. Observability tooling will be added in the next milestone once the instance size or architecture is revisited.

---

## 🗺 Roadmap

```
[✓] PostgreSQL persistence via SQLAlchemy ORM
[✓] REST API with FastAPI
[✓] src-layout package structure
[✓] HTTP-aware custom exceptions (400, 404)
[✓] Docker Compose with healthcheck
[✓] CI pipeline with GitHub Actions
[✓] Unit tests with mocks — 11/11 passing
[✓] Automated CSV backups with timestamp
[✓] Structured logging with run_id
[✓] Docker image published to Docker Hub (iriome2512/expense-tracker)
[✓] CI/CD pipeline — build and push on every push to main
[✓] Prometheus /metrics endpoint
[✓] Grafana dashboards (requests total · request rate · expenses counter · gauge)
[✓] JSON structured logging (replace plaintext format)
[✓] AWS deployment — EC2 t3.micro + Elastic IP (rehosting v1)
[✓] S3 backup storage — CSV backups decoupled from instance lifecycle
[✓] IAM least-privilege — custom policy scoped to backup bucket only
[✓] Per-write backups — S3 upload triggered on every POST and DELETE
[✓] Automated CD — GitHub Actions deploys to EC2 via SSM on every push to main
[✓] Zero open admin ports — SSH replaced by SSM Session Manager

[ ] Custom domain + SSL/TLS with Let's Encrypt
[ ] CloudWatch Agent — application logs shipped to CloudWatch
[ ] Prometheus + Grafana on production EC2 (observability milestone)
[ ] Alembic migrations (replace init_db())
[ ] AWS Secrets Manager for database credentials
[ ] Replatforming — ECS Fargate + RDS + Terraform + full CI/CD pipeline
[ ] Integration tests with real PostgreSQL (testcontainers)
[ ] Rate limiting
[ ] Authentication (API keys or JWT)
```

---

## 👤 Author

Built by **Iriome Santana** as part of a self-taught journey into Site Reliability Engineering and DevOps.

This project is intentionally over-engineered for a simple expense tracker — that's the point. Every layer exists to demonstrate a real engineering principle, not because the problem demands it.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Iriome%20Santana-0077B5?logo=linkedin)](https://www.linkedin.com/in/iriome-santana-socorro)

---

> 💬 **Feedback welcome.** If you're also learning SRE/DevOps and want to discuss architecture decisions, open an issue or reach out on LinkedIn. I'm always happy to learn from other engineers on the same path.