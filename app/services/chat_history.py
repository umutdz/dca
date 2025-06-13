from sqlalchemy.ext.asyncio import AsyncSession


class ChatHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
