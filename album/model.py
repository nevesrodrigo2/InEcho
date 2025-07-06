from typing import Optional
from typing import Annotated
from pydantic import BaseModel, Field
from datetime import datetime


# Define rating as Annotated int with constraints
RatingValue = Annotated[int, Field(ge=0, le=5)]


class RatingCreateRequest(BaseModel):
    title: str
    artist: str
    rating: RatingValue


class RatingResponse(BaseModel):
    title: str
    artist: str
    release_date: str
    genre: str
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    rating: RatingValue


class RatingUpdateRequest(BaseModel):
    title: str
    artist: str
    rating: RatingValue

class RatingDeleteRequest(BaseModel):
    title: str
    artist: str 

class AlbumInfoCreateRequest(BaseModel):
    title: str
    artist: str
    release_date: Optional[str] = None  # ISO format date string
    genre: Optional[str] = None
    image_url: Optional[str] = None  # URL or path to the cover image


class AlbumInfoResponse(BaseModel):
    album_id: int
    title: str
    artist: str
    release_date: Optional[str] = None
    genre: Optional[str] = None
    image_url: Optional[str] = None  # URL or path to the cover image
