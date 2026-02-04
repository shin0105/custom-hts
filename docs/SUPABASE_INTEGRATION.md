# Supabase Integration Guide for HTS Application

This document provides comprehensive guidance for integrating Supabase with the Custom HTS (Home Trading System) application for managing Korean and US stock market data.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Operations](#database-operations)
- [Authentication](#authentication)
- [Storage](#storage)
- [Real-time Features](#real-time-features)
- [Best Practices](#best-practices)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)

## Overview

Supabase provides a PostgreSQL database with built-in authentication, real-time subscriptions, and file storage capabilities. The HTS application uses Supabase to:

- Store Korean and US stock market financial data
- Cache API responses to reduce external API calls
- Manage user preferences and watchlists
- Store historical stock price data
- Handle user authentication and authorization

### Key Features

- **PostgreSQL Database**: 500MB storage limit (free tier)
- **Real-time Subscriptions**: Listen to database changes
- **Row Level Security (RLS)**: Secure data access
- **Storage**: File storage for large datasets
- **Authentication**: Built-in user management

## Installation

### Using UV (Recommended)

```bash
uv add supabase
```

### Using pip

```bash
pip install supabase
```

### Dependencies

The Supabase client automatically includes:
- `postgrest-py`: PostgreSQL REST API client
- `realtime-py`: Real-time subscription client
- `storage3`: Storage bucket management
- `supabase_auth`: Authentication client

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-public-key
SUPABASE_SERVICE_KEY=your-service-role-key  # For admin operations only

# Database Configuration
DATABASE_URL=postgresql://postgres:[password]@[host]:[port]/postgres
```

### Client Initialization

```python
import os
from supabase import create_client, Client
from typing import Optional

class SupabaseClient:
    """Singleton Supabase client for HTS application."""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance."""
        if cls._instance is None:
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")
            
            if not url or not key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
                )
            
            cls._instance = create_client(url, key)
        
        return cls._instance
    
    @classmethod
    def close(cls) -> None:
        """Close the Supabase client and clean up resources."""
        if cls._instance:
            cls._instance.auth.sign_out()
            cls._instance = None

# Usage
supabase = SupabaseClient.get_client()
```

## Database Operations

### Table Structure Examples

#### Korean Stocks Table

```sql
CREATE TABLE korean_stocks (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    market_type VARCHAR(20),  -- KOSPI, KOSDAQ
    current_price DECIMAL(15, 2),
    change_amount DECIMAL(15, 2),
    change_rate DECIMAL(5, 2),
    volume BIGINT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stock_code)
);

CREATE INDEX idx_korean_stocks_code ON korean_stocks(stock_code);
CREATE INDEX idx_korean_stocks_updated ON korean_stocks(updated_at);
```

#### Financial Statements Table

```sql
CREATE TABLE financial_statements (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    market VARCHAR(10) NOT NULL,  -- KR or US
    fiscal_year INTEGER NOT NULL,
    fiscal_quarter INTEGER,  -- NULL for annual
    revenue DECIMAL(20, 2),
    operating_income DECIMAL(20, 2),
    net_income DECIMAL(20, 2),
    total_assets DECIMAL(20, 2),
    total_liabilities DECIMAL(20, 2),
    equity DECIMAL(20, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stock_code, market, fiscal_year, fiscal_quarter)
);

CREATE INDEX idx_financial_statements_code ON financial_statements(stock_code);
CREATE INDEX idx_financial_statements_year ON financial_statements(fiscal_year);
```

### Insert Data

```python
from typing import Dict, List, Any
from datetime import datetime

async def insert_korean_stock_data(
    supabase: Client,
    stock_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Insert Korean stock data into the database.
    
    Args:
        supabase: Supabase client instance
        stock_data: Dictionary containing stock information
        
    Returns:
        Inserted data with generated ID
        
    Raises:
        Exception: If insertion fails
    """
    try:
        response = supabase.table("korean_stocks").insert({
            "stock_code": stock_data["stock_code"],
            "stock_name": stock_data["stock_name"],
            "market_type": stock_data.get("market_type", "KOSPI"),
            "current_price": float(stock_data["current_price"]),
            "change_amount": float(stock_data.get("change_amount", 0)),
            "change_rate": float(stock_data.get("change_rate", 0)),
            "volume": int(stock_data.get("volume", 0)),
            "updated_at": datetime.now().isoformat()
        }).execute()
        
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"Error inserting Korean stock data: {e}")
        raise

async def batch_insert_stocks(
    supabase: Client,
    stocks: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Insert multiple stock records in a single operation.
    
    Args:
        supabase: Supabase client instance
        stocks: List of stock data dictionaries
        
    Returns:
        List of inserted records
    """
    try:
        response = supabase.table("korean_stocks").insert(stocks).execute()
        return response.data
    except Exception as e:
        print(f"Error in batch insert: {e}")
        raise
```

### Select Data

```python
from typing import Optional, List

async def get_stock_by_code(
    supabase: Client,
    stock_code: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve stock data by stock code.
    
    Args:
        supabase: Supabase client instance
        stock_code: Stock code (e.g., "005930" for Samsung)
        
    Returns:
        Stock data dictionary or None if not found
    """
    try:
        response = supabase.table("korean_stocks") \
            .select("*") \
            .eq("stock_code", stock_code) \
            .single() \
            .execute()
        
        return response.data if response.data else None
        
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return None

async def get_top_gainers(
    supabase: Client,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get top gaining stocks by change rate.
    
    Args:
        supabase: Supabase client instance
        limit: Maximum number of results
        
    Returns:
        List of top gaining stocks
    """
    try:
        response = supabase.table("korean_stocks") \
            .select("*") \
            .order("change_rate", desc=True) \
            .limit(limit) \
            .execute()
        
        return response.data
        
    except Exception as e:
        print(f"Error fetching top gainers: {e}")
        return []

async def search_stocks(
    supabase: Client,
    query: str,
    market_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search stocks by name or code with optional market filter.
    
    Args:
        supabase: Supabase client instance
        query: Search query string
        market_type: Optional market type filter (KOSPI, KOSDAQ)
        
    Returns:
        List of matching stocks
    """
    try:
        builder = supabase.table("korean_stocks").select("*")
        
        # Use ilike for case-insensitive pattern matching
        builder = builder.or_(
            f"stock_code.ilike.%{query}%,stock_name.ilike.%{query}%"
        )
        
        if market_type:
            builder = builder.eq("market_type", market_type)
        
        response = builder.limit(50).execute()
        return response.data
        
    except Exception as e:
        print(f"Error searching stocks: {e}")
        return []
```

### Update Data

```python
async def update_stock_price(
    supabase: Client,
    stock_code: str,
    new_price: float,
    change_amount: float,
    change_rate: float,
    volume: int
) -> Optional[Dict[str, Any]]:
    """
    Update stock price and related information.
    
    Args:
        supabase: Supabase client instance
        stock_code: Stock code to update
        new_price: New current price
        change_amount: Price change amount
        change_rate: Price change rate (percentage)
        volume: Trading volume
        
    Returns:
        Updated stock data or None if update fails
    """
    try:
        response = supabase.table("korean_stocks") \
            .update({
                "current_price": new_price,
                "change_amount": change_amount,
                "change_rate": change_rate,
                "volume": volume,
                "updated_at": datetime.now().isoformat()
            }) \
            .eq("stock_code", stock_code) \
            .execute()
        
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"Error updating stock price: {e}")
        return None
```

### Upsert Data

```python
async def upsert_financial_statement(
    supabase: Client,
    statement_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Insert or update financial statement data.
    
    Uses upsert to handle both new records and updates based on
    unique constraint (stock_code, market, fiscal_year, fiscal_quarter).
    
    Args:
        supabase: Supabase client instance
        statement_data: Financial statement data
        
    Returns:
        Upserted record
    """
    try:
        response = supabase.table("financial_statements") \
            .upsert(statement_data) \
            .execute()
        
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"Error upserting financial statement: {e}")
        raise
```

### Delete Data

```python
async def delete_old_stock_data(
    supabase: Client,
    days_old: int = 30
) -> int:
    """
    Delete stock data older than specified days.
    
    Args:
        supabase: Supabase client instance
        days_old: Number of days to keep data
        
    Returns:
        Number of deleted records
    """
    try:
        cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
        
        response = supabase.table("korean_stocks") \
            .delete() \
            .lt("updated_at", cutoff_date) \
            .execute()
        
        return len(response.data) if response.data else 0
        
    except Exception as e:
        print(f"Error deleting old data: {e}")
        return 0
```

### Call PostgreSQL Functions (RPC)

```python
async def get_portfolio_summary(
    supabase: Client,
    user_id: str
) -> Dict[str, Any]:
    """
    Call a custom PostgreSQL function to get portfolio summary.
    
    First, create the function in Supabase SQL editor:
    
    CREATE OR REPLACE FUNCTION get_portfolio_summary(user_id_param UUID)
    RETURNS JSON AS $$
    DECLARE
        result JSON;
    BEGIN
        SELECT json_build_object(
            'total_value', SUM(quantity * current_price),
            'total_gain', SUM((current_price - purchase_price) * quantity),
            'stocks_count', COUNT(*)
        ) INTO result
        FROM user_portfolio
        WHERE user_id = user_id_param;
        
        RETURN result;
    END;
    $$ LANGUAGE plpgsql;
    
    Args:
        supabase: Supabase client instance
        user_id: User identifier
        
    Returns:
        Portfolio summary data
    """
    try:
        response = supabase.rpc(
            "get_portfolio_summary",
            {"user_id_param": user_id}
        ).execute()
        
        return response.data
        
    except Exception as e:
        print(f"Error calling portfolio summary function: {e}")
        return {}
```

## Authentication

### Sign Up and Sign In

```python
from supabase import Client
from typing import Optional

async def sign_up_user(
    supabase: Client,
    email: str,
    password: str
) -> Optional[Dict[str, Any]]:
    """
    Create a new user account.
    
    Args:
        supabase: Supabase client instance
        email: User email address
        password: User password
        
    Returns:
        User data or None if sign up fails
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        return response.user
        
    except Exception as e:
        print(f"Error signing up user: {e}")
        return None

async def sign_in_user(
    supabase: Client,
    email: str,
    password: str
) -> Optional[Dict[str, Any]]:
    """
    Sign in an existing user.
    
    Args:
        supabase: Supabase client instance
        email: User email address
        password: User password
        
    Returns:
        Session data or None if sign in fails
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        return response.session
        
    except Exception as e:
        print(f"Error signing in user: {e}")
        return None

async def sign_out_user(supabase: Client) -> bool:
    """
    Sign out the current user.
    
    Args:
        supabase: Supabase client instance
        
    Returns:
        True if sign out successful, False otherwise
    """
    try:
        supabase.auth.sign_out()
        return True
    except Exception as e:
        print(f"Error signing out user: {e}")
        return False

async def get_current_user(supabase: Client) -> Optional[Dict[str, Any]]:
    """
    Get the currently authenticated user.
    
    Args:
        supabase: Supabase client instance
        
    Returns:
        User data or None if not authenticated
    """
    try:
        response = supabase.auth.get_user()
        return response.user
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None
```

## Storage

### File Upload and Download

```python
from pathlib import Path
from typing import Optional

async def upload_financial_report(
    supabase: Client,
    bucket_name: str,
    file_path: str,
    destination_path: str
) -> Optional[str]:
    """
    Upload a financial report file to Supabase storage.
    
    Args:
        supabase: Supabase client instance
        bucket_name: Storage bucket name
        file_path: Local file path to upload
        destination_path: Destination path in storage
        
    Returns:
        Public URL of uploaded file or None if upload fails
    """
    try:
        with open(file_path, 'rb') as file:
            response = supabase.storage.from_(bucket_name).upload(
                destination_path,
                file
            )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(
            destination_path
        )
        
        return public_url
        
    except Exception as e:
        print(f"Error uploading file: {e}")
        return None

async def download_financial_report(
    supabase: Client,
    bucket_name: str,
    file_path: str,
    local_path: str
) -> bool:
    """
    Download a financial report from Supabase storage.
    
    Args:
        supabase: Supabase client instance
        bucket_name: Storage bucket name
        file_path: File path in storage
        local_path: Local path to save downloaded file
        
    Returns:
        True if download successful, False otherwise
    """
    try:
        data = supabase.storage.from_(bucket_name).download(file_path)
        
        # Save to local file
        with open(local_path, 'wb') as file:
            file.write(data)
        
        return True
        
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

async def list_financial_reports(
    supabase: Client,
    bucket_name: str,
    folder_path: str = ""
) -> List[Dict[str, Any]]:
    """
    List files in a storage bucket folder.
    
    Args:
        supabase: Supabase client instance
        bucket_name: Storage bucket name
        folder_path: Folder path to list files from
        
    Returns:
        List of file metadata
    """
    try:
        response = supabase.storage.from_(bucket_name).list(folder_path)
        return response
    except Exception as e:
        print(f"Error listing files: {e}")
        return []
```

## Real-time Features

### Subscribe to Database Changes

```python
from supabase import Client
from typing import Callable

def subscribe_to_stock_updates(
    supabase: Client,
    callback: Callable[[Dict[str, Any]], None],
    stock_codes: Optional[List[str]] = None
) -> None:
    """
    Subscribe to real-time stock price updates.
    
    Args:
        supabase: Supabase client instance
        callback: Function to call when updates are received
        stock_codes: Optional list of stock codes to filter
    """
    def handle_update(payload: Dict[str, Any]) -> None:
        """Process real-time update payload."""
        event_type = payload.get("eventType")
        new_data = payload.get("new")
        old_data = payload.get("old")
        
        if event_type == "UPDATE" and new_data:
            # Filter by stock codes if specified
            if not stock_codes or new_data.get("stock_code") in stock_codes:
                callback(new_data)
    
    # Subscribe to changes
    channel = supabase.channel("stock-updates")
    channel.on_postgres_changes(
        event="UPDATE",
        schema="public",
        table="korean_stocks",
        callback=handle_update
    ).subscribe()
    
    print("Subscribed to stock updates")

# Usage example
def on_price_update(stock_data: Dict[str, Any]) -> None:
    """Handle stock price update."""
    print(f"Price updated: {stock_data['stock_code']} - {stock_data['current_price']}")

supabase = SupabaseClient.get_client()
subscribe_to_stock_updates(
    supabase,
    on_price_update,
    stock_codes=["005930", "035420"]  # Samsung, NAVER
)
```

## Best Practices

### 1. Connection Management

```python
from contextlib import contextmanager

@contextmanager
def get_supabase_client():
    """Context manager for Supabase client."""
    client = SupabaseClient.get_client()
    try:
        yield client
    finally:
        # Cleanup if needed
        pass

# Usage
with get_supabase_client() as supabase:
    data = supabase.table("korean_stocks").select("*").execute()
```

### 2. Error Handling

```python
from supabase import Client
from postgrest.exceptions import APIError

async def safe_insert(
    supabase: Client,
    table: str,
    data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Safely insert data with comprehensive error handling."""
    try:
        response = supabase.table(table).insert(data).execute()
        return response.data[0] if response.data else None
        
    except APIError as e:
        print(f"API Error: {e.message}")
        print(f"Details: {e.details}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

### 3. Data Validation

```python
from pydantic import BaseModel, validator
from decimal import Decimal

class KoreanStockData(BaseModel):
    """Validation model for Korean stock data."""
    
    stock_code: str
    stock_name: str
    market_type: str
    current_price: Decimal
    change_amount: Decimal
    change_rate: Decimal
    volume: int
    
    @validator('stock_code')
    def validate_stock_code(cls, v):
        """Validate Korean stock code format."""
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Stock code must be 6 digits')
        return v
    
    @validator('market_type')
    def validate_market_type(cls, v):
        """Validate market type."""
        if v not in ['KOSPI', 'KOSDAQ']:
            raise ValueError('Market type must be KOSPI or KOSDAQ')
        return v

# Usage
try:
    stock_data = KoreanStockData(
        stock_code="005930",
        stock_name="Samsung Electronics",
        market_type="KOSPI",
        current_price=Decimal("70000"),
        change_amount=Decimal("1000"),
        change_rate=Decimal("1.45"),
        volume=10000000
    )
    
    await insert_korean_stock_data(supabase, stock_data.dict())
except ValidationError as e:
    print(f"Validation error: {e}")
```

### 4. Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Optional
import time

class CachedSupabaseQuery:
    """Cache Supabase queries to reduce database load."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value with timestamp."""
        self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()

# Usage
cache = CachedSupabaseQuery(ttl_seconds=300)  # 5 minutes

async def get_stock_with_cache(
    supabase: Client,
    stock_code: str
) -> Optional[Dict[str, Any]]:
    """Get stock data with caching."""
    cache_key = f"stock:{stock_code}"
    
    # Check cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data
    
    # Fetch from database
    data = await get_stock_by_code(supabase, stock_code)
    
    # Cache result
    if data:
        cache.set(cache_key, data)
    
    return data
```

## Error Handling

### Common Error Scenarios

```python
from postgrest.exceptions import APIError
from typing import Union, Dict, Any

class SupabaseErrorHandler:
    """Handle common Supabase errors."""
    
    @staticmethod
    def handle_api_error(error: APIError) -> Dict[str, Any]:
        """Parse and handle API errors."""
        error_info = {
            "type": "api_error",
            "message": error.message,
            "details": error.details,
            "code": error.code
        }
        
        # Handle specific error codes
        if error.code == "23505":  # Unique violation
            error_info["user_message"] = "This record already exists"
        elif error.code == "23503":  # Foreign key violation
            error_info["user_message"] = "Related record not found"
        elif error.code == "42P01":  # Table does not exist
            error_info["user_message"] = "Database table not found"
        else:
            error_info["user_message"] = "An error occurred with the database"
        
        return error_info
    
    @staticmethod
    def is_connection_error(error: Exception) -> bool:
        """Check if error is a connection error."""
        return isinstance(error, (ConnectionError, TimeoutError))
    
    @staticmethod
    def should_retry(error: Exception) -> bool:
        """Determine if operation should be retried."""
        # Retry on connection errors or rate limits
        if isinstance(error, APIError):
            return error.code in ["429", "503", "504"]
        return isinstance(error, (ConnectionError, TimeoutError))

# Usage with retry logic
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def resilient_insert(
    supabase: Client,
    table: str,
    data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Insert data with automatic retry on transient errors."""
    try:
        response = supabase.table(table).insert(data).execute()
        return response.data[0] if response.data else None
    except APIError as e:
        error_handler = SupabaseErrorHandler()
        if error_handler.should_retry(e):
            raise  # Retry
        else:
            print(f"Non-retryable error: {error_handler.handle_api_error(e)}")
            return None
```

## Performance Optimization

### 1. Batch Operations

```python
async def batch_upsert_with_chunks(
    supabase: Client,
    table: str,
    data: List[Dict[str, Any]],
    chunk_size: int = 1000
) -> int:
    """
    Upsert data in chunks to avoid payload size limits.
    
    Args:
        supabase: Supabase client instance
        table: Table name
        data: List of records to upsert
        chunk_size: Number of records per chunk
        
    Returns:
        Total number of records upserted
    """
    total_inserted = 0
    
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        try:
            response = supabase.table(table).upsert(chunk).execute()
            total_inserted += len(response.data) if response.data else 0
        except Exception as e:
            print(f"Error upserting chunk {i//chunk_size + 1}: {e}")
    
    return total_inserted
```

### 2. Efficient Queries

```python
async def get_stocks_optimized(
    supabase: Client,
    market_type: str,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get stocks with optimized query and pagination.
    
    Only select necessary columns and use indexes.
    """
    response = supabase.table("korean_stocks") \
        .select("stock_code,stock_name,current_price,change_rate") \
        .eq("market_type", market_type) \
        .order("volume", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()
    
    return response.data
```

### 3. Connection Pooling

For high-traffic applications, consider using a connection pool:

```python
from supabase import create_client
from typing import List
import asyncio

class SupabaseConnectionPool:
    """Simple connection pool for Supabase clients."""
    
    def __init__(self, url: str, key: str, pool_size: int = 5):
        self.url = url
        self.key = key
        self.pool_size = pool_size
        self.pool: List[Client] = []
        self.available: List[Client] = []
        self._lock = asyncio.Lock()
        
        # Initialize pool
        for _ in range(pool_size):
            client = create_client(url, key)
            self.pool.append(client)
            self.available.append(client)
    
    async def acquire(self) -> Client:
        """Acquire a client from the pool."""
        async with self._lock:
            while not self.available:
                await asyncio.sleep(0.1)
            return self.available.pop()
    
    async def release(self, client: Client) -> None:
        """Release a client back to the pool."""
        async with self._lock:
            if client in self.pool and client not in self.available:
                self.available.append(client)
    
    async def close_all(self) -> None:
        """Close all connections in the pool."""
        for client in self.pool:
            client.auth.sign_out()
        self.pool.clear()
        self.available.clear()
```

## Additional Resources

- [Supabase Python Documentation](https://supabase.com/docs/reference/python/introduction)
- [Supabase GitHub Repository](https://github.com/supabase/supabase-py)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

## Support

For issues or questions:
1. Check the [Supabase Community Forums](https://github.com/supabase/supabase/discussions)
2. Review [GitHub Issues](https://github.com/supabase/supabase-py/issues)
3. Consult the internal HTS documentation

---

**Last Updated**: February 2026  
**Version**: 1.0.0
