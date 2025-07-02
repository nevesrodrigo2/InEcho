from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database.core import Base


class Album(Base):
    __tablename__ = 'albums'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    release_date = Column(String, nullable=True)  # ISO format date string
    # URL or path to the cover image
    created_at = Column(Integer, default=lambda: int(
        datetime.now(timezone.utc).timestamp()))
    ratings = relationship("Rating", back_populates="album")

    def __repr__(self):
        return f"<Album(id={self.id}, title='{self.title}', artist='{self.artist}', release_date='{self.release_date}')>"


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    album_id = Column(Integer, ForeignKey('albums.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # Rating value (1-5)
    created_at = Column(Integer, default=lambda: int(
        datetime.now(timezone.utc).timestamp()))
    user = relationship("User", back_populates="ratings")
    album = relationship("Album", back_populates="ratings")

    def __repr__(self):
        return f"<Rating(id={self.id}, user_id={self.user_id}, album_id={self.album_id}, rating={self.rating})>"
