"""
Unit tests for API routes.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.models import TickerPrice


class TestAPIRoutes:
    """Test cases for API routes."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_ticker_price(self):
        """Create mock ticker price data."""
        return TickerPrice(
            id=1,
            ticker="BTC_USD",
            price=45000.50,
            timestamp=1699123456
        )
    
    def test_get_all_prices_success(self, client, mock_ticker_price):
        """Test successful retrieval of all prices."""
        with patch("app.api.routes.PriceService") as mock_service_class:
            mock_service = Mock()
            mock_service.get_all_prices.return_value = [mock_ticker_price]
            mock_service_class.return_value = mock_service
            
            response = client.get("/api/v1/prices?ticker=BTC_USD")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "BTC_USD"
            assert data["count"] == 1
            assert len(data["prices"]) == 1
    
    def test_get_all_prices_missing_ticker(self, client):
        """Test error when ticker parameter is missing."""
        response = client.get("/api/v1/prices")
        
        assert response.status_code == 422  # Validation error
    
    def test_get_latest_price_success(self, client, mock_ticker_price):
        """Test successful retrieval of latest price."""
        with patch("app.api.routes.PriceService") as mock_service_class:
            mock_service = Mock()
            mock_service.get_latest_price.return_value = mock_ticker_price
            mock_service_class.return_value = mock_service
            
            response = client.get("/api/v1/prices/latest?ticker=BTC_USD")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "BTC_USD"
            assert data["price"] == 45000.50
            assert data["timestamp"] == 1699123456
    
    def test_get_latest_price_not_found(self, client):
        """Test retrieval of latest price when no data exists."""
        with patch("app.api.routes.PriceService") as mock_service_class:
            mock_service = Mock()
            mock_service.get_latest_price.return_value = None
            mock_service_class.return_value = mock_service
            
            response = client.get("/api/v1/prices/latest?ticker=BTC_USD")
            
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "BTC_USD"
            assert data["price"] is None
            assert data["timestamp"] is None
    
    def test_get_price_by_date_success(self, client, mock_ticker_price):
        """Test successful retrieval of prices filtered by date."""
        with patch("app.api.routes.PriceService") as mock_service_class:
            mock_service = Mock()
            mock_service.get_price_by_date.return_value = [mock_ticker_price]
            mock_service_class.return_value = mock_service
            
            response = client.get(
                "/api/v1/prices/filter?ticker=BTC_USD&start_date=2023-11-01&end_date=2023-11-30"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["ticker"] == "BTC_USD"
            assert data["count"] == 1
    
    def test_get_price_by_date_invalid_format(self, client):
        """Test error when date format is invalid."""
        with patch("app.api.routes.PriceService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            response = client.get(
                "/api/v1/prices/filter?ticker=BTC_USD&start_date=invalid-date"
            )
            
            assert response.status_code == 400

