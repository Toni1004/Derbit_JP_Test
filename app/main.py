"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from app.api.routes import router
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Deribit Price API",
    description="API for retrieving cryptocurrency index prices from Deribit",
    version="1.0.0"
)

# Include routers
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Deribit Price API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

