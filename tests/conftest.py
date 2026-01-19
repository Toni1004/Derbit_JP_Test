"""
Pytest configuration and fixtures.
"""
import pytest
from unittest.mock import Mock
from app.database import SessionLocal, Base, engine


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)

