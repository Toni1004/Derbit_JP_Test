"""
Unit tests for PriceService.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from app.services.price_service import PriceService
from app.models import TickerPrice


class TestPriceService:
    """Test cases for PriceService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def price_service(self, mock_db):
        """Create PriceService instance with mock database."""
        return PriceService(mock_db)
    
    @pytest.mark.asyncio
    async def test_fetch_and_save_price_success(self, price_service, mock_db):
        """Test successful price fetch and save."""
        # Mock Deribit client response
        mock_price_data = {
            "index_price": 45000.50,
            "timestamp": 1699123456
        }
        
        with patch.object(
            price_service.deribit_client,
            "get_index_price",
            new_callable=AsyncMock,
            return_value=mock_price_data
        ):
            result = await price_service.fetch_and_save_price("BTC_USD")
            
            # Verify database operations
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
            
            # Verify the saved object
            saved_ticker = mock_db.add.call_args[0][0]
            assert saved_ticker.ticker == "BTC_USD"
            assert float(saved_ticker.price) == 45000.50
            assert saved_ticker.timestamp == 1699123456
    
    def test_get_all_prices(self, price_service, mock_db):
        """Test retrieving all prices for a ticker."""
        # Mock database query result
        mock_prices = [
            TickerPrice(id=1, ticker="BTC_USD", price=45000.50, timestamp=1699123456),
            TickerPrice(id=2, ticker="BTC_USD", price=45100.75, timestamp=1699123457),
        ]
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = mock_prices
        mock_db.query.return_value = mock_query
        
        result = price_service.get_all_prices("BTC_USD")
        
        assert len(result) == 2
        assert result[0].ticker == "BTC_USD"
        assert result[0].price == 45000.50
    
    def test_get_latest_price(self, price_service, mock_db):
        """Test retrieving latest price for a ticker."""
        # Mock database query result
        mock_price = TickerPrice(id=1, ticker="BTC_USD", price=45000.50, timestamp=1699123456)
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.first.return_value = mock_price
        mock_db.query.return_value = mock_query
        
        result = price_service.get_latest_price("BTC_USD")
        
        assert result is not None
        assert result.ticker == "BTC_USD"
        assert result.price == 45000.50
    
    def test_get_latest_price_not_found(self, price_service, mock_db):
        """Test retrieving latest price when no data exists."""
        # Mock database query result (no data)
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        result = price_service.get_latest_price("BTC_USD")
        
        assert result is None
    
    def test_get_price_by_date(self, price_service, mock_db):
        """Test retrieving prices filtered by date range."""
        # Mock database query result
        mock_prices = [
            TickerPrice(id=1, ticker="BTC_USD", price=45000.50, timestamp=1699123456),
        ]
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = mock_prices
        mock_db.query.return_value = mock_query
        
        start_date = datetime(2023, 11, 1)
        end_date = datetime(2023, 11, 30)
        
        result = price_service.get_price_by_date("BTC_USD", start_date, end_date)
        
        assert len(result) == 1
        assert result[0].ticker == "BTC_USD"

