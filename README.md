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

- [What is this?](#what-is-this)
- [Architecture](#architecture)
- [Cloud Deployment](#cloud-deployment-aws)
- [Authentication](#-authentication)
- [Project Structure](#-project-structure)
- [SRE Principles in Practice](#sre-principles-in-practice)
- [Tech Stack](#-tech-stack)
- [Monitoring Dashboards](#monitoring-dashboards)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Environment Variables](#environment-variables)
- [Running Tests](#running-tests)
- [Architecture Decision Records](#architecture-decision-records)
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
├── API key authentication + per-owner isolation (core/auth.py)
├── Rate limiting via SlowAPI                  (routes/expenses.py)
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

## Cloud Deployment (AWS)

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

No credentials are stored on the instance. The API authenticates to S3 using the IAM Instance Profile. Deployment commands are sent via SSM — port 22 is not open to the internet.

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
                          curl docker-compose.prod.yml from GitHub
                          docker compose pull
                          docker compose up -d
                          docker image prune -f
```

### Deployment strategy: Rehosting (intentional)

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
          └── No ──▶ write to local disk (development mode)
```

### How to deploy manually

```bash
aws ssm send-command \
  --instance-ids <INSTANCE_ID> \
  --document-name "AWS-RunShellScript" \
  --parameters 'commands=["curl -sL https://raw.githubusercontent.com/Iriome-Santana/expense-tracker-sre/main/deploy/docker-compose.prod.yml -o /app/docker-compose.yml && cd /app && docker compose pull && docker compose --env-file /app/.env up -d"]' \
  --region eu-west-1
```

---

## 🔐 Authentication

The API uses **API key authentication**. Every request to `/expenses/*` requires an `X-API-Key` header. Each key is scoped to an owner — requests only see and modify their own data.

### How it works

```
Request arrives with X-API-Key: abc123
          │
          ▼
FastAPI dependency: get_current_owner()
          │
          ├── Key not found in DB → 401 Unauthorized
          └── Key found → extract owner
                              │
                              ▼
                    All queries filtered by owner
                    User only sees their own expenses
```

### Creating an API key

API keys are created by the admin via a protected endpoint:

```bash
curl -X POST "http://<HOST>:8000/admin/api-keys?owner=your-name" \
  -H "X-Admin-Secret: your-admin-secret"

# Response:
# {"owner": "your-name", "api_key": "64-char-hex-string"}
```

The `ADMIN_SECRET` environment variable controls access to this endpoint. Only the server operator can create keys.

### Using the API

```bash
# Set your key once
export API_KEY="your-api-key-here"

# Use it in every request
curl http://<HOST>:8000/expenses/ -H "X-API-Key: $API_KEY"
```

### Rate limits

```
GET  /expenses/        → 60 requests/minute per IP
GET  /expenses/summary → 60 requests/minute per IP
POST /expenses/        → 20 requests/minute per IP
DELETE /expenses/{id}  → 20 requests/minute per IP
```

Exceeding the limit returns `429 Too Many Requests`.

### Current limitation

This API is designed for **programmatic access**, not browser-based sessions. There is no registration flow or login page. API keys are issued manually by the operator. A browser frontend with JWT-based auth is listed in the roadmap.

---

## 📁 Project Structure

```
expense-tracker/
├── src/
│   └── expense_tracker/
│       ├── main.py                # FastAPI app · lifespan · rate limiter · error handlers
│       ├── models/
│       │   ├── expense.py         # Expense ORM model (with owner column)
│       │   └── api_key.py         # ApiKey ORM model
│       ├── schemas/
│       │   └── expense.py         # Pydantic I/O schemas
│       ├── services/
│       │   ├── expense_service.py # Business logic · owner-scoped queries
│       │   └── backup_service.py  # CSV export → S3 or local disk
│       ├── api/
│       │   └── routes/
│       │       ├── expenses.py    # HTTP endpoints with auth + rate limiting
│       │       └── admin.py       # API key management (admin only)
│       ├── db/
│       │   └── session.py         # Engine · SessionLocal · get_db()
│       └── core/
│           ├── auth.py            # API key validation · get_current_owner()
│           ├── errors.py          # HTTP-aware custom exceptions
│           └── logging.py         # run_id filter · stdout-first logging
├── scripts/
│   └── cli.py
├── tests/
│   ├── conftest.py
│   └── test_expenses.py           # 11 unit tests
├── deploy/
│   ├── Dockerfile
│   ├── docker-compose.yml         # local: api + db + prometheus + grafana
│   └── docker-compose.prod.yml    # production: api + db only
├── .github/
│   └── workflows/
│       └── ci.yml                 # test → build → push → deploy via SSM
├── pyproject.toml
├── .env.example
└── .gitignore
```

---

## SRE Principles in Practice

### 1. Observability

Every session generates a unique `run_id` injected into every log line:

```json
{"timestamp": "2026-04-29T19:18:59Z", "level": "INFO", "message": "Expense created", "run_id": "93c496d2"}
```

Logs are written to stdout in JSON format. Docker captures them and they are accessible via `docker logs`. In production, logs go to stdout only (`LOG_TO_FILE=false`) — no ephemeral file writes inside the container.

### 2. Reliability — Fail Fast

Input validation happens at the decorator level before touching the database:

```python
@validate_expense
def add_expense(self, db, date, description, amount, owner):
    # data is guaranteed valid here
```

### 3. Reliability — Automated Backups to S3

On every write operation (POST or DELETE), expenses are exported to a timestamped CSV and uploaded to S3. Controlled by `S3_BACKUP_BUCKET` — falls back to local disk if not set.

### 4. Operability

- All configuration via environment variables
- `restart: always` in production Compose
- `service_healthy` healthcheck on PostgreSQL
- Deployment via SSM Session Manager — no SSH port open
- CD pipeline updates `docker-compose.yml` from GitHub on every deploy

### 5. Testability

- 11 unit tests, all passing
- Database fully mocked — tests run in ~0.02s with no PostgreSQL
- CI runs on every push and PR to main

---

## Monitoring Dashboards

The application exposes a `/metrics` endpoint for Prometheus. Grafana dashboards are included in the local `docker-compose.yml` but excluded from production to stay within the 1GB RAM limit of a t3.micro.

# Local dashboards
![Grafana Dashboard](docs/images/dashboards.png)

---

## 🛠 Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| API framework | FastAPI 0.129 | Automatic OpenAPI docs, async-ready, Pydantic v2 |
| ORM | SQLAlchemy 2.0 | Clean session lifecycle, pool_pre_ping |
| Validation | Pydantic v2 | Type-safe request/response schemas |
| Database | PostgreSQL 15 | Production-grade, concurrent, typed |
| Authentication | API keys (custom) | Simple, programmatic access, per-owner isolation |
| Rate limiting | SlowAPI | Per-IP limits, 429 on excess |
| Testing | pytest + pytest-cov | Fast, fixture-based, no real DB needed |
| Containerization | Docker Compose | Two-service orchestration (api + db) |
| CI/CD | GitHub Actions | Test → build → push → deploy on every push to main |
| Package mgmt | pyproject.toml | Modern Python standard (PEP 517/518) |
| Cloud compute | AWS EC2 t3.micro | Low cost, Elastic IP, Docker support |
| Cloud storage | AWS S3 | Durable backup storage, lifecycle policy |
| Remote access | AWS SSM Session Manager | Zero open admin ports |

---

## Quick Start

### Option 1 — Docker (recommended)

```bash
git clone https://github.com/Iriome-Santana/expense-tracker-sre.git
cd expense-tracker-sre

cp .env.example .env
nano .env

docker compose --env-file .env -f deploy/docker-compose.yml up --build
```

API available at **http://localhost:8002**
Interactive docs at **http://localhost:8002/docs**

### Option 2 — Local

```bash
pip install -e ".[dev]"

export DB_HOST=localhost DB_NAME=expense_tracker \
       DB_USER=expense_user DB_PASSWORD=expense_pass

uvicorn expense_tracker.main:app --reload
```

### Option 3 — CLI

```bash
pip install -e ".[dev]"
python scripts/cli.py
```

---

## API Reference

| Method | Endpoint | Auth | Description | Success | Error |
|--------|----------|------|-------------|---------|-------|
| `GET` | `/` | No | Health check | 200 | — |
| `GET` | `/expenses/summary` | Yes | Total amount | 200 | 401 |
| `GET` | `/expenses/` | Yes | List expenses | 200 | 401 |
| `POST` | `/expenses/` | Yes | Create expense | 201 | 400, 401 |
| `DELETE` | `/expenses/{id}` | Yes | Delete by ID | 200 | 401, 404 |
| `POST` | `/admin/api-keys` | Admin | Create API key | 201 | 403 |

### Create expense

```bash
curl -X POST http://localhost:8002/expenses/ \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"date": "2026-03-18", "description": "Coffee", "amount": 3.50}'
# 201 → {"message": "Expense added successfully!"}
```

### Unauthorized

```bash
curl http://localhost:8002/expenses/
# 422 → missing X-API-Key header

curl http://localhost:8002/expenses/ -H "X-API-Key: wrong"
# 401 → {"detail": "Invalid or missing API key"}
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_NAME` | `expense_tracker` | Database name |
| `DB_USER` | `expense_user` | Database user |
| `DB_PASSWORD` | `expense_pass` | Database password |
| `POSTGRES_USER` | — | Used by PostgreSQL Docker image |
| `POSTGRES_PASSWORD` | — | Used by PostgreSQL Docker image |
| `POSTGRES_DB` | — | Used by PostgreSQL Docker image |
| `LOG_FILE` | `app.log` | Log file path |
| `LOG_RETENTION_DAYS` | `7` | Days before log deletion |
| `LOG_TO_FILE` | `false` | Write logs to file (local dev only) |
| `BACKUPS_DIR` | `backups` | Local backup directory |
| `S3_BACKUP_BUCKET` | `` | S3 bucket for backups (empty = local disk) |
| `ADMIN_SECRET` | `` | Secret for creating API keys |

---

## Running Tests

```bash
pytest
pytest --cov=expense_tracker --cov-report=term-missing
```

```
11 passed in 0.02s
```

---

## Architecture Decision Records

### Why src-layout instead of flat structure?

Forces Python to always import from the installed package, making the project behave identically locally and inside Docker.

### Why SQLAlchemy ORM instead of raw SQL?

Clean session lifecycle (`get_db()` with `finally: db.close()`), type-safe models, and `pool_pre_ping=True` for silent reconnection of dropped connections.

### Why pyproject.toml instead of requirements.txt?

Defines the entire build system in one file: dependencies, dev dependencies, pytest config, and package discovery. Makes the project installable with `pip install -e .` consistently across local and Docker environments.

### Why mock the database in tests instead of a test database?

Tests run in ~0.02s with no external dependencies. `MagicMock` tests all business logic in isolation, identically on any machine and in CI.

### Why HTTPException subclasses instead of separate exception handlers?

Each error carries its own HTTP semantics (`400`, `404`) without a separate `@app.exception_handler` per type. One `AppError` base class, FastAPI handles the rest.

### Why `depends_on: condition: service_healthy`?

The basic `depends_on` only waits for the container process to start. `pg_isready` polls every 5 seconds and only marks the service healthy when PostgreSQL is genuinely accepting connections.

### Why EC2 + S3 instead of RDS?

RDS adds ~$15–18/month for managed backups and failover. The backup requirement is covered by `backup_service.py` writing CSVs to S3 on every write. PostgreSQL in a container eliminates network latency, reduces cost by ~65%, and keeps the environment identical to local. This decision would be revisited for multi-instance deployments or point-in-time recovery requirements.

### Why rehosting instead of replatforming from the start?

Validates the containerised stack in AWS with minimal risk. Preserves AWS credits — a t3.micro costs a fraction of ECS Fargate + RDS. Documented as intentional, not as the final state.

### Why SSM Session Manager instead of SSH for deployment?

SSH required port 22 open to `0.0.0.0/0` because GitHub Actions uses unpredictable IP ranges. SSM eliminates the open port entirely — the EC2 connects outbound to SSM, GitHub Actions sends commands through the AWS API. Zero attack surface for the deployment path.

### Why API keys instead of JWT?

This API is designed for programmatic access, not browser-based sessions. API keys are simpler to implement, easier to rotate, and sufficient for the current use case. JWT would be the correct choice if the project required browser login, token expiration, or refresh flows — which would also require a users table, registration endpoint, and frontend. That scope is listed in the roadmap.

### Security tradeoff: credentials in User Data

Database credentials are stored in a `.env` file on the EC2, created during bootstrap. Acceptable for a single-instance personal project. Would be replaced with AWS Secrets Manager in a multi-person environment. IAM policy follows least-privilege: only `PutObject`, `GetObject`, and `ListBucket` on the specific backup bucket.

### Why Prometheus and Grafana are excluded from production?

A t3.micro has 1GB RAM. Running api + db + prometheus + grafana pushes the instance into swap. Production runs only the two essential services (~600MB combined). Observability tooling is the next milestone.

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
[✓] Docker image published to Docker Hub
[✓] CI/CD pipeline — build and push on every push to main
[✓] Prometheus /metrics endpoint
[✓] Grafana dashboards
[✓] JSON structured logging
[✓] AWS deployment — EC2 t3.micro + Elastic IP (rehosting v1)
[✓] S3 backup storage — decoupled from instance lifecycle
[✓] IAM least-privilege — custom policy scoped to backup bucket
[✓] Per-write backups — S3 upload on every POST and DELETE
[✓] Automated CD — GitHub Actions deploys via SSM on every push to main
[✓] Zero open admin ports — SSH replaced by SSM Session Manager
[✓] Rate limiting — SlowAPI, per-IP, 429 on excess
[✓] API key authentication — per-owner data isolation
[✓] stdout-only logging in production — no ephemeral file writes
[✓] Alembic migrations (replace init_db() + manual ALTER TABLE)


[ ] Custom domain + SSL/TLS with Let's Encrypt
[ ] CloudWatch Agent — logs shipped to CloudWatch
[ ] Prometheus + Grafana on production EC2
[ ] AWS Secrets Manager for database credentials
[ ] Browser frontend with JWT auth (registration + login flow)
[ ] Replatforming — ECS Fargate + RDS + Terraform + full CI/CD
[ ] Integration tests with real PostgreSQL (testcontainers)
```

---

## 👤 Author

Built by **Iriome Santana** as part of a self-taught journey into Site Reliability Engineering and DevOps.

This project is intentionally over-engineered for a simple expense tracker — that's the point. Every layer exists to demonstrate a real engineering principle, not because the problem demands it.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Iriome%20Santana-0077B5?logo=linkedin)](https://www.linkedin.com/in/iriome-santana-socorro)

---

> 💬 **Feedback welcome.** If you're also learning SRE/DevOps and want to discuss architecture decisions, open an issue or reach out on LinkedIn.