from app.db.postgres.models.base import BaseModel
from sqlalchemy import Column, String, Boolean


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    # TODO: should be extended with more fields for user profile

    def __repr__(self):
        return f"<User(email={self.email})>"
