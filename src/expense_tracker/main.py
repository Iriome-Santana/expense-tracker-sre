import logging
import uuid

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from expense_tracker.api.routes.expenses import router as expenses_router
from expense_tracker.core.logging import setup_logging
from expense_tracker.db.session import init_db

RUN_ID = str(uuid.uuid4())[:8]

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(run_id=RUN_ID)
    init_db()
    logging.info(f"Starting Expense Tracker API with run ID: {RUN_ID}")
    yield
    logging.info(f"Shutting down Expense Tracker API with run ID: {RUN_ID}")


app = FastAPI(title="Expense Tracker API", 
              lifespan=lifespan,
              description="REST API for personal expense tracking with SRE principles.",
              version="0.1.0")

app.include_router(expenses_router)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unexpected error on {request.url} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )



@app.get("/")
def home():
    return {"message": "Welcome to the Expense Tracker API!"}
