from fastapi import Depends, FastAPI
from typing import List, Annotated
from sqlalchemy.orm import Session
from auth import auth
from database.core import get_db, Base, engine
from fastapi import status


app = FastAPI()
app.include_router(auth.router)

Base.metadata.create_all(bind=engine)

db_session = Annotated[Session, Depends(get_db)]


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Welcome to InEcho API!"}
