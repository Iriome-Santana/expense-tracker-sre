from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from expense_tracker.api.routes.expenses import router as expenses_router
from expense_tracker.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Expense Tracker API", 
              lifespan=lifespan,
              description="REST API for personal expense tracking with SRE principles.",
              version="0.1.0")

app.include_router(expenses_router)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )



@app.get("/")
def home():
    return {"message": "Welcome to the Expense Tracker API!"}
