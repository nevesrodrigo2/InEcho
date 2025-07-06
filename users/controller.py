from typing import Annotated
from fastapi import Depends, HTTPException, Request, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from auth.service import CurrentUser
from database.core import DbSession
from rate_limiting import limiter
from . import service
from . import model


router = APIRouter(
    prefix='/user',
    tags={'user'}
)


@router.put('/change-password', status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def change_password(request: Request, password_change: model.PasswordChange, db: DbSession, current_user: CurrentUser):
    service.change_password(password_change, db, current_user)
