from fastapi import Depends, FastAPI
from typing import Annotated
from sqlalchemy.orm import Session
from auth import controller as auth
from users import controller as users
from album import controller as album
from database.core import get_db, Base, engine
from fastapi import status
from app_logging import configure_logging
import logging

configure_logging('debug')

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(album.router)

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db_session = Annotated[Session, Depends(get_db)]


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    logging.info("Root endpoint accessed")
    return {"message": "Welcome to InEcho API!"}
