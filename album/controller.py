from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from database.core import DbSession
from rate_limiting import limiter
from starlette import status
from . import service
from . import model
from auth.service import CurrentUser


router = APIRouter(
    prefix='/album',
    tags=['album']
)


@router.get('/ratings', response_model=List[model.RatingResponse])
@limiter.limit("10/minute")
async def get_ratings(request: Request, db_session: DbSession, current_user: CurrentUser):
    return service.get_ratings(db_session, current_user)


@router.post('/rate-album', status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def rate_album(request: Request, rating: model.RatingCreateRequest, db_session: DbSession, current_user: CurrentUser):
    return service.rate_album(rating, db_session, current_user)


@router.delete('/delete-rating', status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_rating(request: Request, rating: model.RatingDeleteRequest, db_session: DbSession, current_user: CurrentUser):
    return service.delete_rating(rating, db_session, current_user)


@router.delete('/delete-all-ratings', status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_all_ratings(request: Request, db_session: DbSession, current_user: CurrentUser):
    return service.delete_all_ratings(db_session, current_user)


@router.put('/change-rating', status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def change_rating(request: Request, new_rating: model.RatingUpdateRequest, db_session: DbSession, current_user: CurrentUser):
    return service.change_rating(new_rating, db_session, current_user)
