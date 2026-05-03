import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from expense_tracker.core.auth import generate_api_key
from expense_tracker.db.session import get_db
from expense_tracker.models.api_key import ApiKey

router = APIRouter(prefix="/admin", tags=["admin"])

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "")


def verify_admin(x_admin_secret: str = Header(...)):
    """Solo el admin puede crear API keys."""
    if not ADMIN_SECRET or x_admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/api-keys", status_code=201)
def create_api_key(
    owner: str,
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin)
):
    key = generate_api_key()
    api_key = ApiKey(key=key, owner=owner)
    db.add(api_key)
    db.commit()
    logging.info(f"API key created for owner: {owner}")
    return {"owner": owner, "api_key": key}