from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..controllers import menu_items as controller
from ..schemas import menu_items as schema
from ..dependencies.database import get_db
from ..models import menu_items as model
from sqlalchemy import func
from ..models import order_details as order_detail_model
from ..models import ratings as rating_model
from ..models import orders as order_model

router = APIRouter(
    tags=['Menu Items'],
    prefix="/menu-items"
)


@router.post("/", response_model=schema.MenuItem, status_code=status.HTTP_201_CREATED)
def create(request: schema.MenuItemCreate, db: Session = Depends(get_db)):
    return controller.create(db=db, request=request)


@router.get("/", response_model=List[schema.MenuItem])
def read_all(db: Session = Depends(get_db)):
    return controller.read_all(db)


@router.get("/{item_id}", response_model=schema.MenuItem)
def read_one(item_id: int, db: Session = Depends(get_db)):
    return controller.read_one(db, item_id=item_id)


@router.put("/{item_id}", response_model=schema.MenuItem)
def update(item_id: int, request: schema.MenuItemUpdate, db: Session = Depends(get_db)):
    return controller.update(db=db, request=request, item_id=item_id)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(item_id: int, db: Session = Depends(get_db)):
    return controller.delete(db=db, item_id=item_id)

@router.get("/category/{category}", response_model=List[schema.MenuItem])
def get_by_category(category: str, db: Session = Depends(get_db)):
    """Get all menu items by food category"""
    items = db.query(model.MenuItem).filter(model.MenuItem.food_category == category).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No items found in category: {category}")
    return items

@router.get("/search/", response_model=List[schema.MenuItem])
def search_menu_items(
    q: str, 
    db: Session = Depends(get_db)
):
    """Search menu items by dish name or ingredients"""
    items = db.query(model.MenuItem).filter(
        (model.MenuItem.dish.like(f"%{q}%")) | 
        (model.MenuItem.ingredients.like(f"%{q}%"))
    ).all()
    return items

@router.get("/price-range/", response_model=List[schema.MenuItem])
def get_by_price_range(
    min_price: float, 
    max_price: float, 
    db: Session = Depends(get_db)
):
    """Get menu items within price range"""
    from decimal import Decimal
    items = db.query(model.MenuItem).filter(
        model.MenuItem.price >= Decimal(str(min_price)),
        model.MenuItem.price <= Decimal(str(max_price))
    ).all()
    return items

@router.get("/public/", response_model=List[schema.MenuItem])
def view_public_menu(db: Session = Depends(get_db)):
    """View menu without any authentication"""
    return controller.read_all(db)

@router.get("/public/search/", response_model=List[schema.MenuItem])
def public_search_menu(q: str, db: Session = Depends(get_db)):
    """Search menu without authentication"""
    items = db.query(model.MenuItem).filter(
        (model.MenuItem.dish.like(f"%{q}%")) | 
        (model.MenuItem.ingredients.like(f"%{q}%"))
    ).all()
    return items

@router.get("/sort/price/", response_model=List[schema.MenuItem])
def sort_menu_by_price(
    order: str = "asc", 
    db: Session = Depends(get_db)
):
    """Sort menu items by price (asc or desc)"""
    if order.lower() == "desc":
        items = db.query(model.MenuItem).order_by(model.MenuItem.price.desc()).all()
    else:
        items = db.query(model.MenuItem).order_by(model.MenuItem.price.asc()).all()
    return items

@router.get("/categories/", status_code=status.HTTP_200_OK)
def list_all_categories(db: Session = Depends(get_db)):
    """List all unique food categories with item counts"""
    categories = db.query(
        model.MenuItem.food_category, 
        func.count(model.MenuItem.id).label("item_count")
    ).filter(model.MenuItem.food_category.isnot(None)).group_by(model.MenuItem.food_category).all()
    
    return [
        {"category": cat[0], "item_count": cat[1]} 
        for cat in categories if cat[0]
    ]


@router.get("/popular/", response_model=List[schema.MenuItem])
def get_popular_items(
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """Get most popular menu items based on order frequency"""
    popular_items = db.query(
        model.MenuItem,
        func.sum(order_detail_model.OrderDetail.number_of_items).label("total_ordered")
    ).join(
        order_detail_model.OrderDetail, 
        model.MenuItem.id == order_detail_model.OrderDetail.menu_item_id
    ).group_by(
        model.MenuItem.id
    ).order_by(
        func.sum(order_detail_model.OrderDetail.number_of_items).desc()
    ).limit(limit).all()
    
    if not popular_items:
        return controller.read_all(db)[:limit]
    
    return [item[0] for item in popular_items]


@router.get("/recommended/", response_model=List[schema.MenuItem])
def get_recommended_items(
    customer_id: Optional[int] = None,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """Get recommended items based on customer's past orders or high ratings"""
    if customer_id:
        # Get customer's past order items
        past_items = db.query(order_detail_model.OrderDetail.menu_item_id).join(
            order_model.Order
        ).filter(
            order_model.Order.customer_id == customer_id
        ).distinct().all()
        
        past_ids = [item[0] for item in past_items]
        
        # Find similar category items
        if past_ids:
            past_categories = db.query(model.MenuItem.food_category).filter(
                model.MenuItem.id.in_(past_ids)
            ).distinct().all()
            
            categories = [cat[0] for cat in past_categories if cat[0]]
            
            recommended = db.query(model.MenuItem).filter(
                model.MenuItem.food_category.in_(categories),
                ~model.MenuItem.id.in_(past_ids)
            ).limit(limit).all()
            
            if recommended:
                return recommended
    
    # Fallback: highest rated items
    highly_rated = db.query(model.MenuItem).join(
        rating_model.Rating, 
        model.MenuItem.id == rating_model.Rating.menu_item_id
    ).group_by(
        model.MenuItem.id
    ).order_by(
        func.avg(rating_model.Rating.score).desc()
    ).limit(limit).all()
    
    if highly_rated:
        return highly_rated
    
    # Second fallback: all items
    return controller.read_all(db)[:limit]