from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres.models.chat_history import ChatHistory
from app.repositories.postgres.base import PostgresRepository


class PostgreChatHistoryRepository(PostgresRepository[ChatHistory]):
    """PostgreSQL implementation of ChatHistory repository."""

    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model_class=ChatHistory)

    async def get_chat_history(self, user_id: int) -> List[ChatHistory]:
        """Get chat history for a user"""
        return await self.get_multi(user_id=user_id)
