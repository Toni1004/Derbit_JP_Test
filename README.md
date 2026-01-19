# Deribit Price API

A backend application for fetching and storing cryptocurrency index prices from Deribit exchange, with a RESTful API for querying the stored data.

## Features

- **Automated Price Fetching**: Periodically fetches BTC_USD and ETH_USD index prices from Deribit every minute using Celery
- **RESTful API**: FastAPI-based API with three endpoints for querying price data
- **PostgreSQL Database**: Stores ticker prices with timestamps for historical analysis
- **Docker Support**: Complete containerization with separate containers for app, database, and Celery workers
- **Unit Tests**: Comprehensive test coverage for main components
- **Clean Architecture**: Well-structured codebase following SOLID principles

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Application configuration
│   ├── database.py             # Database connection and session management
│   ├── models.py               # SQLAlchemy database models
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoints
│   │   └── schemas.py          # Pydantic schemas for request/response
│   ├── clients/
│   │   ├── __init__.py
│   │   └── deribit_client.py   # Deribit API client using aiohttp
│   ├── services/
│   │   ├── __init__.py
│   │   └── price_service.py    # Business logic for price operations
│   └── tasks/
│       ├── __init__.py
│       ├── celery_app.py       # Celery application configuration
│       ├── price_tasks.py      # Celery tasks for price fetching
│       └── beat_schedule.py    # Periodic task schedule
├── tests/
│   ├── __init__.py
│   ├── test_api_routes.py      # API endpoint tests
│   ├── test_price_service.py   # Service layer tests
│   └── test_deribit_client.py  # Client tests
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Application Docker image
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if running database separately)
- Redis (for Celery broker/backend)

## Quick Start with Docker

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Derbit_JP_Test
   ```

2. **Create environment file** (optional, defaults are set):
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Check service status**:
   ```bash
   docker-compose ps
   ```

5. **View logs**:
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f app
   docker-compose logs -f celery_worker
   docker-compose logs -f celery_beat
   ```

6. **Access the API**:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Local Development Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**:
   ```bash
   # Create database
   createdb derbit_db
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database and Redis settings
   ```

4. **Start Redis** (for Celery):
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:7-alpine
   
   # Or install and run locally
   redis-server
   ```

5. **Run database migrations** (tables are auto-created on first run):
   ```bash
   python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
   ```

6. **Start the FastAPI application**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Start Celery worker** (in a separate terminal):
   ```bash
   celery -A app.tasks.celery_app worker --loglevel=info
   ```

8. **Start Celery beat** (in another terminal):
   ```bash
   celery -A app.tasks.celery_app beat --loglevel=info
   ```

## API Endpoints

All endpoints require a `ticker` query parameter (e.g., `BTC_USD`, `ETH_USD`).

### 1. Get All Prices
**GET** `/api/v1/prices?ticker=BTC_USD`

Returns all saved prices for the specified ticker.

**Response**:
```json
{
  "ticker": "BTC_USD",
  "count": 100,
  "prices": [
    {
      "id": 1,
      "ticker": "BTC_USD",
      "price": 45000.50,
      "timestamp": 1699123456
    },
    ...
  ]
}
```

### 2. Get Latest Price
**GET** `/api/v1/prices/latest?ticker=BTC_USD`

Returns the most recent price for the specified ticker.

**Response**:
```json
{
  "ticker": "BTC_USD",
  "price": 45000.50,
  "timestamp": 1699123456
}
```

### 3. Get Prices by Date Range
**GET** `/api/v1/prices/filter?ticker=BTC_USD&start_date=2023-11-01&end_date=2023-11-30`

Returns prices filtered by date range. Date format: ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS).

**Query Parameters**:
- `ticker` (required): Currency ticker
- `start_date` (optional): Start date in ISO format
- `end_date` (optional): End date in ISO format

**Response**:
```json
{
  "ticker": "BTC_USD",
  "count": 30,
  "prices": [
    {
      "id": 1,
      "ticker": "BTC_USD",
      "price": 45000.50,
      "timestamp": 1699123456
    },
    ...
  ]
}
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_price_service.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_USER` | PostgreSQL user | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `DB_NAME` | Database name | `derbit_db` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database number | `0` |
| `DERIBIT_API_URL` | Deribit API base URL | `https://www.deribit.com/api/v2` |

## Design Decisions

### Architecture

**Layered Architecture**: The application follows a clean layered architecture:
- **API Layer** (`app/api/`): Handles HTTP requests/responses, validation, and routing
- **Service Layer** (`app/services/`): Contains business logic and orchestrates data operations
- **Data Layer** (`app/models.py`, `app/database.py`): Manages database models and connections
- **Client Layer** (`app/clients/`): Handles external API interactions

This separation ensures:
- **Testability**: Each layer can be tested independently with mocks
- **Maintainability**: Changes in one layer don't affect others
- **Reusability**: Services can be used by different API endpoints or tasks

### Database Design

**Single Table with Indexes**: The `TickerPrice` model uses a single table with:
- Composite index on `(ticker, timestamp)` for efficient queries
- Individual indexes on `ticker` and `timestamp` for flexible filtering
- `Numeric(20, 8)` for price storage to maintain precision

**Rationale**: 
- Simple schema fits the current requirements
- Indexes optimize the most common query patterns
- Easy to extend if additional fields are needed

### Async/Sync Hybrid Approach

**aiohttp for External API**: The Deribit client uses `aiohttp` for asynchronous HTTP requests, providing:
- Better performance for I/O-bound operations
- Non-blocking requests when fetching multiple prices
- Efficient resource utilization

**Sync Database Operations**: SQLAlchemy ORM operations are synchronous because:
- Simplicity in service layer code
- SQLAlchemy's async support requires additional setup
- Current load doesn't require async database operations

**Celery Task Bridge**: The Celery task uses `asyncio.run_until_complete()` to bridge sync Celery tasks with async service methods, allowing reuse of async client code.

### Error Handling

**Graceful Degradation**: 
- API errors return appropriate HTTP status codes with descriptive messages
- Celery tasks log errors but don't crash the worker
- Database connection errors are handled at the dependency injection level

**Validation**:
- Pydantic schemas validate all API inputs/outputs
- Query parameters are validated by FastAPI
- Date parsing includes error handling with user-friendly messages

### Configuration Management

**Pydantic Settings**: Using `pydantic-settings` for configuration provides:
- Type validation
- Environment variable loading
- Default values
- `.env` file support

**No Global Variables**: All configuration is accessed through the `Settings` class instance, making it:
- Testable (can override settings in tests)
- Predictable (single source of truth)
- Type-safe

### Testing Strategy

**Unit Tests with Mocks**: Tests use mocks to:
- Isolate components under test
- Avoid external API calls during testing
- Run tests quickly without database setup
- Test error scenarios safely

**Test Coverage**:
- API routes (request/response validation, error handling)
- Service layer (business logic, data operations)
- Client layer (API interaction, error handling)

### Containerization

**Multi-Container Setup**: Separate containers for:
- **app**: FastAPI application
- **db**: PostgreSQL database
- **redis**: Message broker for Celery
- **celery_worker**: Background task processor
- **celery_beat**: Periodic task scheduler

**Benefits**:
- Isolation of concerns
- Easy scaling of individual components
- Development/production parity
- Simplified deployment

### Code Quality

**No Global Variables**: All state is managed through:
- Dependency injection (FastAPI's `Depends`)
- Class instances
- Configuration objects

**OOP Principles**:
- Single Responsibility: Each class has one clear purpose
- Dependency Inversion: High-level modules depend on abstractions (services depend on database sessions, not specific implementations)
- Open/Closed: Easy to extend (add new tickers, new endpoints) without modifying existing code

**Naming Conventions**:
- Clear, descriptive names (`PriceService`, `DeribitClient`, `TickerPrice`)
- Consistent patterns (services end with `Service`, clients end with `Client`)
- Self-documenting code

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
1. Ensure PostgreSQL is running: `docker-compose ps db`
2. Check database credentials in `.env`
3. Verify network connectivity between containers

### Celery Tasks Not Running

If prices aren't being fetched:
1. Check Celery worker logs: `docker-compose logs celery_worker`
2. Check Celery beat logs: `docker-compose logs celery_beat`
3. Verify Redis is accessible: `docker-compose ps redis`
4. Ensure beat schedule is loaded: Check `app/tasks/celery_app.py` imports `beat_schedule`

### API Not Responding

1. Check app logs: `docker-compose logs app`
2. Verify port 8000 is not in use
3. Check health endpoint: `curl http://localhost:8000/health`

## Future Improvements

- Add authentication/authorization for API endpoints
- Implement rate limiting
- Add database migrations with Alembic
- Add monitoring and logging (e.g., Prometheus, ELK stack)
- Implement caching for frequently accessed data
- Add WebSocket support for real-time price updates
- Support for additional cryptocurrencies
- Add pagination for large result sets
- Implement database connection pooling optimization

## License

This project is created as a test assignment.

## Author

Created as part of a junior backend developer position test assignment.

