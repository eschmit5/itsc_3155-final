from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from ..controllers import orders as controller
from ..schemas import orders as schema
from ..dependencies.database import engine, get_db
from ..models import customers as customer_model

router = APIRouter(
    tags=['Orders'],
    prefix="/orders"
)


@router.post("/", response_model=schema.Order, status_code=status.HTTP_201_CREATED)
def create(request: schema.OrderCreate, db: Session = Depends(get_db)):
    customer = db.query(customer_model.Customer).filter(customer_model.Customer.id == request.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return controller.create(db=db, request=request)


@router.get("/", response_model=list[schema.Order])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}", response_model=schema.Order)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.Order)
def update(item_id: int, request: schema.OrderUpdate, db: Session = Depends(get_db)):
    if request.customer_id:
        customer = db.query(customer_model.Customer).filter(customer_model.Customer.id == request.customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)


@router.get("/customer/{customer_id}", response_model=List[schema.Order])
def get_orders_by_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(customer_model.Customer).filter(customer_model.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return controller.get_orders_by_customer(db=db, customer_id=customer_id)


@router.get("/tracking/{tracking_number}", response_model=schema.Order)
def get_order_by_tracking(tracking_number: str, db: Session = Depends(get_db)):
    return controller.get_order_by_tracking(db=db, tracking_number=tracking_number)
