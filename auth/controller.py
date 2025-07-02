from typing import Annotated
from fastapi import Depends, HTTPException, Request, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from . import service
from . import model
from database.core import DbSession
from ..rate_limiting import limiter

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register_user(request: Request, db: DbSession, register_user_request: model.RegisterUserRequest):
    service.register_user(register_user_request, db)


@router.post('/token', response_model=model.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    service.authenticate_user(form_data.username, form_data.password, db)
