"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel
from typing import Optional


class TickerPriceResponse(BaseModel):
    """Response schema for ticker price data."""
    id: int
    ticker: str
    price: float
    timestamp: int
    
    class Config:
        from_attributes = True
        populate_by_name = True


class PriceListResponse(BaseModel):
    """Response schema for list of prices."""
    ticker: str
    count: int
    prices: list[TickerPriceResponse]


class LatestPriceResponse(BaseModel):
    """Response schema for latest price."""
    ticker: str
    price: Optional[float] = None
    timestamp: Optional[int] = None


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None

