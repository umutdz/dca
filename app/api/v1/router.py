from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    pdf,
)

api_router = APIRouter()

api_router.include_router(pdf.router, tags=["pdf"])
api_router.include_router(auth.router, tags=["auth"])
