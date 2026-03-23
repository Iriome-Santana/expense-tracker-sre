import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from expense_tracker.api.routes.expenses import router as expenses_router
from expense_tracker.core.logging import setup_logging
from expense_tracker.db.session import init_db, SessionLocal
from expense_tracker.services.backup_service import backup_expenses

RUN_ID = str(uuid.uuid4())[:8]


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(run_id=RUN_ID)
    init_db()
    logging.info(f"API started - run_id: {RUN_ID}")

    db = SessionLocal()
    try:
        backup_expenses(db)
    finally:
        db.close()

    yield

    logging.info(f"API shutdown - run_id: {RUN_ID}")


app = FastAPI(
    title="Expense Tracker API",
    description="REST API for personal expense tracking with SRE principles.",
    version="0.1.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)

app.include_router(expenses_router)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unexpected error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


@app.get("/")
def home():
    return {"message": "Welcome to the Expense Tracker API!"}