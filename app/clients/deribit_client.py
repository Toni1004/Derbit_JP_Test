"""
Deribit API client for fetching cryptocurrency index prices.
"""
import aiohttp
from typing import Dict, Optional
from app.config import settings


class DeribitClient:
    """
    Client for interacting with Deribit API to fetch index prices.
    
    Uses aiohttp for asynchronous HTTP requests.
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize Deribit client.
        
        Args:
            base_url: Base URL for Deribit API. Defaults to settings value.
        """
        self.base_url = base_url or settings.deribit_api_url
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create aiohttp session.
        
        Returns:
            aiohttp.ClientSession instance
        """
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get_index_price(self, currency: str) -> Dict[str, float]:
        """
        Fetch index price for a given currency from Deribit.
        
        Args:
            currency: Currency code (e.g., 'BTC', 'ETH')
            
        Returns:
            Dictionary containing 'index_price' and 'timestamp'
            
        Raises:
            aiohttp.ClientError: If request fails
            ValueError: If currency is invalid or response is malformed
        """
        session = await self._get_session()
        url = f"{self.base_url}/public/get_index_price"
        params = {"index_name": f"{currency}_USD"}
        
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                if data.get("error"):
                    error_msg = data.get("error", {}).get("message", "Unknown error")
                    raise ValueError(f"Deribit API error: {error_msg}")
                
                result = data.get("result", {})
                index_price = result.get("index_price")
                timestamp = result.get("timestamp")
                
                if index_price is None or timestamp is None:
                    raise ValueError("Invalid response format from Deribit API")
                
                # Deribit returns timestamp in milliseconds, convert to seconds (UNIX timestamp)
                timestamp_value = int(timestamp)
                # If timestamp is in milliseconds (13 digits), convert to seconds
                timestamp_seconds = timestamp_value // 1000 if timestamp_value > 1e10 else timestamp_value
                
                return {
                    "index_price": float(index_price),
                    "timestamp": timestamp_seconds
                }
        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"Failed to fetch price from Deribit: {str(e)}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

