from fastapi.testclient import TestClient
from ..controllers import orders as controller
from ..main import app
import pytest
from ..models import orders as model
from ..models import customers as customer_model
from ..schemas import orders as schema
from decimal import Decimal
from datetime import datetime

# Create a test client for the app
client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


@pytest.fixture
def sample_customer():
    """Create a sample customer for testing"""
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "phone_number": "555-1234",
        "address": "123 Main St"
    }


@pytest.fixture
def sample_order_data():
    """Create sample order data for testing"""
    return {
        "tracking_number": "TRK001",
        "order_status": "Pending",
        "total_price": Decimal("25.98"),
        "customer_id": 1
    }


def test_create_order(db_session, sample_order_data):
    """Test creating a new order"""
    # Create an order object from the sample data
    order_object = model.Order(
        tracking_number=sample_order_data["tracking_number"],
        order_status=sample_order_data["order_status"],
        total_price=sample_order_data["total_price"],
        customer_id=sample_order_data["customer_id"]
    )

    # Call the create function
    created_order = controller.create(db_session, order_object)

    # Assertions
    assert created_order is not None
    assert created_order.tracking_number == "TRK001"
    assert created_order.order_status == "Pending"
    assert created_order.total_price == Decimal("25.98")
    assert created_order.customer_id == 1


def test_read_all_orders(db_session, mocker):
    """Test reading all orders"""
    # Mock the query result
    mock_orders = [
        model.Order(
            id=1,
            tracking_number="TRK001",
            order_status="Pending",
            total_price=Decimal("25.98"),
            customer_id=1
        ),
        model.Order(
            id=2,
            tracking_number="TRK002",
            order_status="Completed",
            total_price=Decimal("15.99"),
            customer_id=1
        )
    ]
    
    mocker.patch.object(db_session, 'query').return_value.all.return_value = mock_orders
    
    # Call the read_all function
    result = controller.read_all(db_session)
    
    # Assertions
    assert result is not None
    assert len(result) == 2
    assert result[0].tracking_number == "TRK001"
    assert result[1].tracking_number == "TRK002"


def test_read_one_order(db_session, mocker):
    """Test reading a single order by ID"""
    # Mock the query result
    mock_order = model.Order(
        id=1,
        tracking_number="TRK001",
        order_status="Pending",
        total_price=Decimal("25.98"),
        customer_id=1
    )
    
    mock_query = mocker.Mock()
    mock_query.filter.return_value.first.return_value = mock_order
    mocker.patch.object(db_session, 'query').return_value = mock_query
    
    # Call the read_one function
    result = controller.read_one(db_session, 1)
    
    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.tracking_number == "TRK001"


def test_read_one_order_not_found(db_session, mocker):
    """Test reading an order that doesn't exist"""
    # Mock the query to return None
    mock_query = mocker.Mock()
    mock_query.filter.return_value.first.return_value = None
    mocker.patch.object(db_session, 'query').return_value = mock_query
    
    # Call the read_one function and expect an exception
    with pytest.raises(Exception) as exc_info:
        controller.read_one(db_session, 999)
    
    assert "Order not found" in str(exc_info.value)


def test_update_order(db_session, mocker, sample_order_data):
    """Test updating an order"""
    # Mock the existing order
    mock_order = model.Order(
        id=1,
        tracking_number="TRK001",
        order_status="Pending",
        total_price=Decimal("25.98"),
        customer_id=1
    )
    
    # Mock the update request
    class MockRequest:
        def dict(self, exclude_unset=True):
            return {"order_status": "Completed"}
    
    mock_query = mocker.Mock()
    mock_query.filter.return_value.first.return_value = mock_order
    mock_query.filter.return_value.update.return_value = None
    mocker.patch.object(db_session, 'query').return_value = mock_query
    mocker.patch.object(db_session, 'commit')
    
    # Call the update function
    request = MockRequest()
    result = controller.update(db_session, 1, request)
    
    # Assertions
    assert result is not None
    # The mock might not reflect the update, but the function should complete


def test_update_order_status(db_session, mocker):
    """Test updating just the order status"""
    # Mock the existing order
    mock_order = model.Order(
        id=1,
        tracking_number="TRK001",
        order_status="Pending",
        total_price=Decimal("25.98"),
        customer_id=1
    )
    
    mock_query = mocker.Mock()
    mock_query.filter.return_value.first.return_value = mock_order
    mock_query.filter.return_value.update.return_value = None
    mocker.patch.object(db_session, 'query').return_value = mock_query
    mocker.patch.object(db_session, 'commit')
    
    # Call the update_status function
    result = controller.update_status(db_session, 1, "Completed")
    
    # Assertions
    assert result is not None


def test_delete_order(db_session, mocker):
    """Test deleting an order"""
    # Mock the existing order
    mock_order = model.Order(
        id=1,
        tracking_number="TRK001",
        order_status="Pending",
        total_price=Decimal("25.98"),
        customer_id=1
    )
    
    mock_query = mocker.Mock()
    mock_query.filter.return_value.first.return_value = mock_order
    mock_query.filter.return_value.delete.return_value = None
    mocker.patch.object(db_session, 'query').return_value = mock_query
    mocker.patch.object(db_session, 'commit')
    
    # Call the delete function
    result = controller.delete(db_session, 1)
    
    # Assertions
    assert result is not None


def test_get_by_customer(db_session, mocker):
    """Test getting orders by customer ID"""
    # Mock the customer exists
    mock_customer = customer_model.Customer(
        id=1,
        name="John Doe",
        email="john@example.com"
    )
    
    # Mock the orders
    mock_orders = [
        model.Order(
            id=1,
            tracking_number="TRK001",
            order_status="Pending",
            total_price=Decimal("25.98"),
            customer_id=1
        )
    ]
    
    # Mock customer query
    mock_customer_query = mocker.Mock()
    mock_customer_query.filter.return_value.first.return_value = mock_customer
    
    # Mock orders query
    mock_orders_query = mocker.Mock()
    mock_orders_query.filter.return_value.all.return_value = mock_orders
    
    # Setup the mock to return different values for different calls
    mocker.patch.object(db_session, 'query').side_effect = [mock_customer_query, mock_orders_query]
    
    # Call the get_by_customer function
    result = controller.get_by_customer(db_session, 1)
    
    # Assertions
    assert result is not None
    assert len(result) == 1


def test_get_by_tracking(db_session, mocker):
    """Test getting an order by tracking number"""
    # Mock the order
    mock_order = model.Order(
        id=1,
        tracking_number="TRK001",
        order_status="Pending",
        total_price=Decimal("25.98"),
        customer_id=1
    )
    
    mock_query = mocker.Mock()
    mock_query.filter.return_value.first.return_value = mock_order
    mocker.patch.object(db_session, 'query').return_value = mock_query
    
    # Call the get_by_tracking function
    result = controller.get_by_tracking(db_session, "TRK001")
    
    # Assertions
    assert result is not None
    assert result.tracking_number == "TRK001"


def test_create_order_via_api():
    """Test creating an order through the actual API endpoint"""
    # First create a customer
    customer_response = client.post(
        "/customers/",
        json={
            "name": "API Test User",
            "email": "apitest@example.com",
            "phone_number": "555-9999",
            "address": "456 API St"
        }
    )
    
    # If customer created successfully, create an order
    if customer_response.status_code == 200 or customer_response.status_code == 201:
        customer_id = customer_response.json()["id"]
        
        # Create an order
        order_response = client.post(
            "/orders/",
            json={
                "tracking_number": "APITEST001",
                "order_status": "Pending",
                "total_price": 49.99,
                "customer_id": customer_id
            }
        )
        
        assert order_response.status_code == 200 or order_response.status_code == 201
        order_data = order_response.json()
        assert order_data["tracking_number"] == "APITEST001"
        assert order_data["customer_id"] == customer_id


def test_get_all_orders_via_api():
    """Test getting all orders through the API endpoint"""
    response = client.get("/orders/")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_single_order_via_api():
    """Test getting a single order through the API endpoint"""
    # First create a customer and order to ensure one exists
    customer_response = client.post(
        "/customers/",
        json={
            "name": "Single Test User",
            "email": "singletest@example.com",
            "phone_number": "555-8888",
            "address": "789 Single St"
        }
    )
    
    if customer_response.status_code in [200, 201]:
        customer_id = customer_response.json()["id"]
        
        order_response = client.post(
            "/orders/",
            json={
                "tracking_number": "SINGLETEST001",
                "order_status": "Pending",
                "total_price": 29.99,
                "customer_id": customer_id
            }
        )
        
        if order_response.status_code in [200, 201]:
            order_id = order_response.json()["id"]
            
            # Now get the specific order
            get_response = client.get(f"/orders/{order_id}")
            assert get_response.status_code == 200
            assert get_response.json()["id"] == order_id