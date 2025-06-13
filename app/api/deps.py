from app.db.postgres.session import get_db
from app.services.auth import AuthService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chat_history import ChatHistoryService


def depends_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)


def depends_chat_history_service(db: AsyncSession = Depends(get_db)) -> ChatHistoryService:
    return ChatHistoryService(db)
