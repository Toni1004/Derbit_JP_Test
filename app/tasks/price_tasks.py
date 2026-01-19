"""
Celery tasks for periodic price fetching.
"""
import asyncio
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.services.price_service import PriceService


@celery_app.task(name="fetch_and_save_prices")
def fetch_and_save_prices():
    """
    Celery task to fetch and save BTC_USD and ETH_USD prices.
    
    This task runs periodically (every minute) to fetch index prices
    from Deribit and save them to the database.
    """
    db = SessionLocal()
    try:
        service = PriceService(db)
        
        # Run async operations in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Fetch and save BTC_USD price
            loop.run_until_complete(service.fetch_and_save_price("BTC_USD"))
            
            # Fetch and save ETH_USD price
            loop.run_until_complete(service.fetch_and_save_price("ETH_USD"))
            
            # Close service connections
            loop.run_until_complete(service.close())
        finally:
            loop.close()
            
    except Exception as e:
        # Log error but don't fail the task completely
        print(f"Error fetching prices: {str(e)}")
        raise
    finally:
        db.close()

