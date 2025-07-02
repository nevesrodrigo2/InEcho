from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey
from database.core import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(Integer, default=lambda: int(
        datetime.now(timezone.utc).timestamp()))

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', email='{self.email}')>"
