from fastapi import APIRouter, Depends, Path
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from models import Users
from passlib.context import CryptContext

router = APIRouter(prefix='/auth', tags=['Login'])

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str


@router.get('/auth', status_code=201)
async def get_user(db: db_dependency, request: CreateUserRequest):
    model = Users(
        email=request.email,
        username=request.username,
        first_name=request.first_name,
        last_name=request.last_name,
        hashed_password=bcrypt_context.hash(request.password),
        role=request.role,
        is_active=True
    )
    db.add(model)
    db.commit()
