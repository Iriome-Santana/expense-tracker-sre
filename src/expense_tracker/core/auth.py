import logging
import secrets
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from expense_tracker.db.session import get_db
from expense_tracker.models.api_key import ApiKey


def get_current_owner(
    x_api_key: str = Header(..., description="API key for authentication"),
    db: Session = Depends(get_db)
) -> str:
    """
    Dependencia de FastAPI que valida la API key y devuelve el owner.
    Se inyecta en cada endpoint que requiere autenticación.
    
    Header(...) significa que es obligatorio.
    Si no viene el header → FastAPI devuelve 422 automáticamente.
    Si la key no existe en BD → devolvemos 401.
    """
    api_key = db.query(ApiKey).filter(ApiKey.key == x_api_key).first()
    
    if not api_key:
        logging.warning(f"Invalid API key attempt")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )
    
    logging.info(f"Authenticated request from owner: {api_key.owner}")
    return api_key.owner


def generate_api_key() -> str:
    """Genera una API key segura de 32 bytes en hexadecimal."""
    return secrets.token_hex(32)