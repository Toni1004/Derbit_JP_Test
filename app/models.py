"""
Database models for storing ticker price data.
"""
from sqlalchemy import Column, String, Numeric, BigInteger, Index
from app.database import Base


class TickerPrice(Base):
    """
    Model for storing ticker price data from Deribit.
    
    Attributes:
        id: Primary key (auto-increment)
        ticker: Currency ticker (e.g., 'BTC_USD', 'ETH_USD')
        price: Current index price of the currency
        timestamp: UNIX timestamp when the price was recorded
    """
    __tablename__ = "ticker_prices"
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    price = Column(Numeric(20, 8), nullable=False)
    timestamp = Column(BigInteger, nullable=False, index=True)
    
    # Composite index for efficient queries by ticker and timestamp
    __table_args__ = (
        Index('idx_ticker_timestamp', 'ticker', 'timestamp'),
    )
    
    def __repr__(self) -> str:
        return f"<TickerPrice(ticker={self.ticker}, price={self.price}, timestamp={self.timestamp})>"

