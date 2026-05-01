from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from ..dependencies.database import get_db
from ..models import menu_items as menu_model
from ..models import orders as order_model
from ..models import order_details as order_detail_model
from ..models import customers as customer_model
from ..schemas import orders as order_schema
from ..schemas import order_details as order_detail_schema

router = APIRouter(
    tags=['Guest Checkout'],
    prefix="/guest"
)

guest_carts = {}  # In-memory storage for guest carts

@router.post("/cart", status_code=status.HTTP_201_CREATED)
def create_guest_cart():
    """Create a new guest cart"""
    cart_id = str(uuid.uuid4())
    guest_carts[cart_id] = {
        "items": [],
        "created_at": datetime.utcnow(),
        "total": 0.00
    }
    return {"cart_id": cart_id, "message": "Guest cart created successfully"}

@router.post("/cart/{cart_id}/items", status_code=status.HTTP_200_OK)
def add_item_to_cart(
    cart_id: str, 
    menu_item_id: int, 
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    """Add an item to guest cart"""
    if cart_id not in guest_carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    
    # Verify menu item exists
    menu_item = db.query(menu_model.MenuItem).filter(menu_model.MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found")
    
    # Add item to cart
    cart = guest_carts[cart_id]
    existing_item = next((item for item in cart["items"] if item["menu_item_id"] == menu_item_id), None)
    
    if existing_item:
        existing_item["quantity"] += quantity
        existing_item["subtotal"] = existing_item["quantity"] * float(menu_item.price)
    else:
        cart["items"].append({
            "menu_item_id": menu_item_id,
            "dish": menu_item.dish,
            "price": float(menu_item.price),
            "quantity": quantity,
            "subtotal": quantity * float(menu_item.price)
        })
    
    # Update cart total
    cart["total"] = sum(item["subtotal"] for item in cart["items"])

    return {
        "cart_id": cart_id,
        "items": cart["items"],
        "total": cart["total"],
        "item_count": len(cart["items"])
    }

@router.get("/cart/{cart_id}", status_code=status.HTTP_200_OK)
def view_guest_cart(cart_id: str):
    """View guest cart contents"""
    if cart_id not in guest_carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    
    cart = guest_carts[cart_id]
    return {
        "cart_id": cart_id,
        "items": cart["items"],
        "total": cart["total"],
        "created_at": cart["created_at"]
    }

@router.delete("/cart/{cart_id}/items/{menu_item_id}", status_code=status.HTTP_200_OK)
def remove_item_from_cart(cart_id: str, menu_item_id: int):
    """Remove an item from guest cart"""
    if cart_id not in guest_carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    
    cart = guest_carts[cart_id]
    cart["items"] = [item for item in cart["items"] if item["menu_item_id"] != menu_item_id]
    cart["total"] = sum(item["subtotal"] for item in cart["items"])
    
    return {
        "cart_id": cart_id,
        "items": cart["items"],
        "total": cart["total"]
    }

@router.post("/checkout", status_code=status.HTTP_201_CREATED)
def guest_checkout(
    cart_id: str,
    customer_name: str,
    customer_email: str,
    customer_phone: Optional[str] = None,
    customer_address: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Convert guest cart to order"""
    if cart_id not in guest_carts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
    
    cart = guest_carts[cart_id]
    if not cart["items"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")
    
    # Create customer account from guest info
    new_customer = customer_model.Customer(
        name=customer_name,
        email=customer_email,
        phone_number=customer_phone,
        address=customer_address
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    # Create order
    tracking_number = f"TRK{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{new_customer.id}"
    new_order = order_model.Order(
        tracking_number=tracking_number,
        order_status="Pending",
        total_price=cart["total"],
        customer_id=new_customer.id,
        order_date=datetime.utcnow()
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Create order details
    for item in cart["items"]:
        order_detail = order_detail_model.OrderDetail(
            order_id=new_order.id,
            menu_item_id=item["menu_item_id"],
            number_of_items=item["quantity"]
        )
        db.add(order_detail)
    
    db.commit()
    
    # Clear guest cart
    del guest_carts[cart_id]
    
    return {
        "message": "Order placed successfully",
        "order_id": new_order.id,
        "tracking_number": tracking_number,
        "customer_id": new_customer.id,
        "total_price": float(cart["total"])
    }

