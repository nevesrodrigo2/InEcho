from auth.service import CurrentUser
from . import model
from sqlalchemy.orm import Session
from entities.user import User
from auth.service import verify_password, get_password_hash
from fastapi import HTTPException, status
from utils.current_user_utils import get_current_db_user
import logging


def check_password(password: str, hashed_password: str) -> bool:
    return verify_password(password, hashed_password)


def change_password(password_change: model.PasswordChange, db: Session, current_user: CurrentUser):
    '''
    Changes the current user's password
    '''
    db_user = get_current_db_user(db, current_user)
    user_id = db_user.id

    if not db_user:
        logging.error(f'User: {user_id} does not exist.')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if not check_password(password_change.old_password, db_user.hashed_password):
        logging.error('Old password is incorrect.')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if password_change.new_password != password_change.new_password_confirmation:
        logging.error('New password does not match the confirmation password.')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if password_change.old_password == password_change.new_password:
        logging.error('New password can not be the same as the old password.')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    logging.info(f'User: {user_id} password was changed successfully')
    db_user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()
