from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from ..controllers import ratings as controller
from ..schemas import ratings as schema
from ..dependencies.database import get_db

router = APIRouter(
    tags=['Ratings'],
    prefix="/ratings"
)


@router.post("/", response_model=schema.Rating, status_code=status.HTTP_201_CREATED)
def create(request: schema.RatingCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=List[schema.Rating])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}", response_model=schema.Rating)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Rating)
def update(item_id: int, request: schema.RatingUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)