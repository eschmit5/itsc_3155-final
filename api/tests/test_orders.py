from fastapi.testclient import TestClient
import sys
import os

# Add the api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the app using the module path
try:
    from api.main import app
except ImportError:
    from main import app

import pytest

client = TestClient(app)


def test_server_running():
    """Test that the server responds to a basic request"""
    response = client.get("/orders/")
    # May return 200 or 404 depending on data, but shouldn't crash
    assert response.status_code in [200, 404]


def test_menu_items_endpoint():
    """Test menu items endpoint"""
    response = client.get("/menu-items/")
    assert response.status_code in [200, 404]


def test_guest_cart():
    """Test guest cart creation"""
    response = client.post("/guest/cart")
    assert response.status_code == 201


def test_customers_endpoint():
    """Test customers endpoint"""
    response = client.get("/customers/")
    assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])