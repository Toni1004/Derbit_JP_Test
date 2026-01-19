"""
Unit tests for DeribitClient.
"""
import pytest
import aiohttp
from unittest.mock import AsyncMock, patch
from app.clients.deribit_client import DeribitClient


class TestDeribitClient:
    """Test cases for DeribitClient."""
    
    @pytest.mark.asyncio
    async def test_get_index_price_success(self):
        """Test successful price fetch from Deribit API."""
        mock_response_data = {
            "jsonrpc": "2.0",
            "result": {
                "index_price": 45000.50,
                "timestamp": 1699123456000
            },
            "usIn": 1699123456000000,
            "usOut": 1699123456001000,
            "usDiff": 1000,
            "testnet": False
        }
        
        async with DeribitClient() as client:
            with patch("aiohttp.ClientSession.get") as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value=mock_response_data)
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)
                mock_get.return_value = mock_response
                
                result = await client.get_index_price("BTC")
                
                assert result["index_price"] == 45000.50
                assert result["timestamp"] == 1699123456000
    
    @pytest.mark.asyncio
    async def test_get_index_price_api_error(self):
        """Test handling of API error response."""
        mock_response_data = {
            "jsonrpc": "2.0",
            "error": {
                "code": 10001,
                "message": "Invalid currency"
            }
        }
        
        async with DeribitClient() as client:
            with patch("aiohttp.ClientSession.get") as mock_get:
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value=mock_response_data)
                mock_response.__aenter__ = AsyncMock(return_value=mock_response)
                mock_response.__aexit__ = AsyncMock(return_value=None)
                mock_get.return_value = mock_response
                
                with pytest.raises(ValueError, match="Deribit API error"):
                    await client.get_index_price("INVALID")

