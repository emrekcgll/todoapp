from fastapi import APIRouter, Depends, Path
from http.client import HTTPException
from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from models import Todos
from database import SessionLocal


router = APIRouter(prefix='/todos', tags=['Todo'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3, max_length=12)
    description: str
    priority: int = Field(gt=0, lt=0)
    complete: bool


@router.get('/')
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@router.get('/todo/{id}', status_code=200)
async def get_by_id(db: db_dependency, id: int = Path(gt=0)):
    model = db.query(Todos).filter(Todos.id == id).first()
    if model is not None:
        return model
    raise HTTPException(status_code=404, detail='Todo not found.')


@router.post('/todo', status_code=201)
async def create(db: db_dependency, request: TodoRequest):
    model = Todos(**request.model_dump())
    db.add(model)
    db.commit()


@router.put('/todo/{id}', status_code=204)
async def update(db: db_dependency, request: TodoRequest, id: int = Path(gt=0)):
    model = db.query(Todos).filter(Todos.id == id).first()
    if model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    model.title = request.title
    model.description = request.description
    model.priotry = request.priotry
    model.complete = request.complete

    db.add(model)
    db.commit()


@router.delete('/todo/{id}', status_code=204)
async def delete(db: db_dependency, id: int = Path(gt=0)):
    model = db.query(Todos).filter(Todos.id == id).first()
    if model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos.id == id).delete()
    db.commit()
