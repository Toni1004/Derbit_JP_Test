"""
FastAPI routes for ticker price API.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.services.price_service import PriceService
from app.api.schemas import (
    PriceListResponse,
    LatestPriceResponse,
    TickerPriceResponse,
    ErrorResponse
)

router = APIRouter(prefix="/api/v1", tags=["prices"])


@router.get(
    "/prices",
    response_model=PriceListResponse,
    summary="Get all saved prices for a ticker",
    description="Retrieves all saved price data for the specified currency ticker"
)
async def get_all_prices(
    ticker: str = Query(..., description="Currency ticker (e.g., BTC_USD, ETH_USD)"),
    db: Session = Depends(get_db)
):
    """
    Get all saved prices for a given ticker.
    
    Args:
        ticker: Currency ticker (required query parameter)
        db: Database session dependency
        
    Returns:
        List of all prices for the ticker
    """
    service = PriceService(db)
    prices = service.get_all_prices(ticker)
    
    return PriceListResponse(
        ticker=ticker,
        count=len(prices),
        prices=[TickerPriceResponse.model_validate(price) for price in prices]
    )


@router.get(
    "/prices/latest",
    response_model=LatestPriceResponse,
    summary="Get latest price for a ticker",
    description="Retrieves the most recent price for the specified currency ticker"
)
async def get_latest_price(
    ticker: str = Query(..., description="Currency ticker (e.g., BTC_USD, ETH_USD)"),
    db: Session = Depends(get_db)
):
    """
    Get the latest price for a given ticker.
    
    Args:
        ticker: Currency ticker (required query parameter)
        db: Database session dependency
        
    Returns:
        Latest price data or null if no data exists
    """
    service = PriceService(db)
    latest_price = service.get_latest_price(ticker)
    
    if latest_price is None:
        return LatestPriceResponse(ticker=ticker, price=None, timestamp=None)
    
    return LatestPriceResponse(
        ticker=ticker,
        price=float(latest_price.price),
        timestamp=latest_price.timestamp
    )


@router.get(
    "/prices/filter",
    response_model=PriceListResponse,
    summary="Get prices filtered by date",
    description="Retrieves prices for a ticker within a specified date range"
)
async def get_price_by_date(
    ticker: str = Query(..., description="Currency ticker (e.g., BTC_USD, ETH_USD)"),
    start_date: Optional[str] = Query(None, description="Start date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"),
    end_date: Optional[str] = Query(None, description="End date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"),
    db: Session = Depends(get_db)
):
    """
    Get prices for a ticker filtered by date range.
    
    Args:
        ticker: Currency ticker (required query parameter)
        start_date: Start date in ISO format (optional)
        end_date: End date in ISO format (optional)
        db: Database session dependency
        
    Returns:
        List of prices within the date range
    """
    service = PriceService(db)
    
    # Parse dates if provided
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid start_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            )
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid end_date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            )
    
    prices = service.get_price_by_date(ticker, start_dt, end_dt)
    
    return PriceListResponse(
        ticker=ticker,
        count=len(prices),
        prices=[TickerPriceResponse.model_validate(price) for price in prices]
    )

