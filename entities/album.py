from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from database.core import Base


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    album_id = Column(Integer, ForeignKey('albums.id'), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    rating = Column(Integer, nullable=False)  # Rating out of 5

    user = relationship("User", back_populates="ratings")
    album = relationship("Album", back_populates="ratings")

    __table_args__ = (
        UniqueConstraint('user_id', 'album_id', name='uix_user_album'),
    )


class Album(Base):
    __tablename__ = 'albums'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    release_date = Column(String, nullable=True)  # ISO format date string
    genre = Column(String, nullable=True)
    image_url = Column(String, nullable=True)  # URL or path to the cover image

    ratings = relationship("Rating", back_populates="album")

    __table_args__ = (
        UniqueConstraint('title', 'artist', name='uix_album'),
    )

    def __repr__(self):
        return f"<AlbumInfo(id={self.id}, title='{self.title}', artist='{self.artist}')>"
