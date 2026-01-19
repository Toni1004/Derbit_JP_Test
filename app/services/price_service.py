"""
Service layer for managing ticker price data.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import TickerPrice
from app.clients.deribit_client import DeribitClient


class PriceService:
    """
    Service for managing ticker price operations.
    
    Handles fetching prices from Deribit and storing/retrieving from database.
    """
    
    def __init__(self, db: Session):
        """
        Initialize price service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.deribit_client = DeribitClient()
    
    async def fetch_and_save_price(self, ticker: str) -> TickerPrice:
        """
        Fetch price from Deribit API and save to database.
        
        Args:
            ticker: Currency ticker (e.g., 'BTC_USD', 'ETH_USD')
            
        Returns:
            Saved TickerPrice instance
            
        Raises:
            ValueError: If ticker format is invalid or API call fails
        """
        # Extract currency from ticker (e.g., 'BTC' from 'BTC_USD')
        currency = ticker.split('_')[0].upper()
        
        # Fetch price from Deribit
        price_data = await self.deribit_client.get_index_price(currency)
        
        # Create database record
        ticker_price = TickerPrice(
            ticker=ticker,
            price=price_data["index_price"],
            timestamp=price_data["timestamp"]
        )
        
        self.db.add(ticker_price)
        self.db.commit()
        self.db.refresh(ticker_price)
        
        return ticker_price
    
    def get_all_prices(self, ticker: str) -> List[TickerPrice]:
        """
        Get all saved prices for a given ticker.
        
        Args:
            ticker: Currency ticker (e.g., 'BTC_USD', 'ETH_USD')
            
        Returns:
            List of TickerPrice instances, ordered by timestamp descending
        """
        return self.db.query(TickerPrice).filter(
            TickerPrice.ticker == ticker
        ).order_by(desc(TickerPrice.timestamp)).all()
    
    def get_latest_price(self, ticker: str) -> Optional[TickerPrice]:
        """
        Get the most recent price for a given ticker.
        
        Args:
            ticker: Currency ticker (e.g., 'BTC_USD', 'ETH_USD')
            
        Returns:
            Most recent TickerPrice instance or None if not found
        """
        return self.db.query(TickerPrice).filter(
            TickerPrice.ticker == ticker
        ).order_by(desc(TickerPrice.timestamp)).first()
    
    def get_price_by_date(
        self, 
        ticker: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[TickerPrice]:
        """
        Get prices for a ticker filtered by date range.
        
        Args:
            ticker: Currency ticker (e.g., 'BTC_USD', 'ETH_USD')
            start_date: Start of date range (optional)
            end_date: End of date range (optional)
            
        Returns:
            List of TickerPrice instances within the date range
        """
        query = self.db.query(TickerPrice).filter(
            TickerPrice.ticker == ticker
        )
        
        if start_date:
            start_timestamp = int(start_date.timestamp())
            query = query.filter(TickerPrice.timestamp >= start_timestamp)
        
        if end_date:
            end_timestamp = int(end_date.timestamp())
            query = query.filter(TickerPrice.timestamp <= end_timestamp)
        
        return query.order_by(desc(TickerPrice.timestamp)).all()
    
    async def close(self):
        """Close the Deribit client session."""
        await self.deribit_client.close()

