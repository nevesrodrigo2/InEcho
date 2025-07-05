from fastapi import HTTPException
from database.core import DbSession
from auth.service import CurrentUser
from entities.user import User
from messages.error_messages import USER_NOT_FOUND


def get_current_db_user(db: DbSession, current_user: CurrentUser):
    user_id = current_user.user_id
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        return db_user
    else:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND)
