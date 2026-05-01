from fastapi import APIRouter, Depends, FastAPI, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from ..controllers import orders as controller
from ..schemas import orders as schema
from ..dependencies.database import engine, get_db
from ..models import customers as customer_model
from ..models import order_details as order_detail_model
from ..models import menu_items as menu_model
from ..models import orders as order_model
from decimal import Decimal
from datetime import datetime, timedelta

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

@router.get("/{order_id}/total", status_code=status.HTTP_200_OK)
def calculate_order_total(order_id: int, db: Session = Depends(get_db)):
    """Calculate and return order total including all items"""
    # Verify order exists
    order = controller.read_one(db, order_id)
    
    # Get all order details
    order_details = db.query(order_detail_model.OrderDetail).filter(
        order_detail_model.OrderDetail.order_id == order_id
    ).all()
    
    if not order_details:
        return {"order_id": order_id, "total": float(order.total_price), "items": []}
    
    total = Decimal('0.00')
    items_detail = []
    
    for detail in order_details:
        menu_item = db.query(menu_model.MenuItem).filter(
            menu_model.MenuItem.id == detail.menu_item_id
        ).first()
        if menu_item:
            item_total = menu_item.price * detail.number_of_items
            total += item_total
            items_detail.append({
                "menu_item_id": detail.menu_item_id,
                "dish": menu_item.dish,
                "price": float(menu_item.price),
                "quantity": detail.number_of_items,
                "subtotal": float(item_total)
            })
    
    # Update order total if different
    if total != order.total_price:
        order.total_price = total
        db.commit()
        db.refresh(order)
    
    return {
        "order_id": order_id,
        "total": float(total),
        "items": items_detail
    }

@router.get("/{order_id}/eta", status_code=status.HTTP_200_OK)
def get_order_eta(order_id: int, db: Session = Depends(get_db)):
    """Get estimated time of arrival for order based on status and queue"""
    order = controller.read_one(db, order_id)
    
    # Base preparation times by order status
    eta_map = {
        "Pending": 15,
        "Preparing": 10,
        "Ready": 0,
        "Completed": 0,
        "Cancelled": None
    }
    
    base_minutes = eta_map.get(order.order_status, 20)
    
    if base_minutes is None:
        return {"order_id": order_id, "eta": "Order cancelled", "status": order.order_status}
    
    if base_minutes == 0:
        return {"order_id": order_id, "eta": "Ready for pickup", "status": order.order_status}
    
    # Calculate queue delay based on other orders in same status
    queue_count = db.query(order_model.Order).filter(
        order_model.Order.order_status == order.order_status,
        order_model.Order.id < order_id
    ).count()
    
    queue_delay = queue_count * 2  # 2 minutes per order ahead in queue
    
    total_minutes = base_minutes + queue_delay
    estimated_time = datetime.utcnow() + timedelta(minutes=total_minutes)
    
    return {
        "order_id": order_id,
        "status": order.order_status,
        "total_price": float(order.total_price),
        "eta_minutes": total_minutes,
        "estimated_ready_time": estimated_time.isoformat(),
        "queue_position": queue_count + 1
    }