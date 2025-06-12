from sqlalchemy import Column, Integer, Text, ForeignKey, UUID

from app.db.postgres.models.base import BaseModel


class ChatHistory(BaseModel):
    """Chat history model for storing user questions and AI responses"""

    __tablename__ = "chat_history"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    session_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self) -> str:
        return f"<ChatHistory(user_id={self.user_id}, session_id={self.session_id})>"
