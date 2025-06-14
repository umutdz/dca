from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres.session import get_db, get_db_context
from app.services.auth import AuthService
from app.services.chat_history import ChatHistoryService
from app.services.pdf import PDFService


def depends_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


def depends_chat_history_service(db: AsyncSession = Depends(get_db)) -> ChatHistoryService:
    return ChatHistoryService(db)


def depends_pdf_service() -> PDFService:
    return PDFService()


async def get_current_user(token: str):
    if token.lower().startswith("bearer "):
        token = token[7:]
    async with get_db_context() as db:
        current_user = await AuthService(db).get_user(token)
        return current_user
