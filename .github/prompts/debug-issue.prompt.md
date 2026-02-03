---
agent: 'debugging-specialist'
model: Claude Sonnet 4.5 (copilot)
tools: ['semantic_search', 'get_errors', 'run_in_terminal', 'grep_search']
description: 'Provide debugging assistance for HTS application issues'
---

# Debugging Assistant for HTS Application

Your goal is to help identify, diagnose, and resolve issues in the HTS trading application, focusing on financial data accuracy, API integrations, and performance problems.

## Debugging Approach

### Issue Analysis Process
1. **Symptom Identification**: What is the observed behavior vs expected behavior?
2. **Context Gathering**: When does the issue occur? Which market? Which components?
3. **Data Validation**: Is the issue with data accuracy, display, or processing?
4. **System Impact**: Does it affect Korean market, US market, or both?
5. **Reproduction Steps**: Can the issue be consistently reproduced?

### Common Issue Categories

#### Financial Data Issues
- **Price Accuracy**: Incorrect stock prices or currency conversions
- **Calculation Errors**: Wrong financial ratios or percentage calculations
- **Data Freshness**: Stale or outdated market data
- **Currency Formatting**: Incorrect display of KRW vs USD values
- **Market Hours**: Data updating outside of trading hours

#### API Integration Issues
- **Rate Limiting**: Exceeding API call limits
- **Authentication**: API key expiration or invalid credentials
- **Data Parsing**: Incorrect handling of API responses
- **Network Timeouts**: Slow or failed API calls
- **Data Transformation**: Errors in converting between data formats

#### Performance Issues
- **Slow Loading**: Components taking too long to render
- **Memory Leaks**: React components not cleaning up properly
- **Database Queries**: Slow or inefficient database operations
- **Real-time Updates**: Laggy or missing live data updates
- **Bundle Size**: Large JavaScript bundles affecting load times

## Frontend Debugging

### React Component Debugging

#### Common React Issues
```typescript
// Issue: Component not re-rendering with new data
const StockPrice = ({ symbol }) => {
  const [price, setPrice] = useState(0);
  
  useEffect(() => {
    fetchStockPrice(symbol).then(setPrice);
  }, []); // Missing dependency: symbol
  
  return <div>${price}</div>;
};

// Solution: Add proper dependencies
const StockPrice = ({ symbol }) => {
  const [price, setPrice] = useState(0);
  
  useEffect(() => {
    fetchStockPrice(symbol).then(setPrice);
  }, [symbol]); // Include symbol in dependencies
  
  return <div>${price}</div>;
};
```

#### Memory Leak Detection
```typescript
// Issue: Memory leak with interval
const RealTimePrice = ({ symbol }) => {
  const [price, setPrice] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      fetchCurrentPrice(symbol).then(setPrice);
    }, 1000);
    // Missing cleanup function
  }, [symbol]);
  
  return <div>{price}</div>;
};

// Solution: Proper cleanup
const RealTimePrice = ({ symbol }) => {
  const [price, setPrice] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      fetchCurrentPrice(symbol).then(setPrice);
    }, 1000);
    
    return () => clearInterval(interval); // Cleanup
  }, [symbol]);
  
  return <div>{price}</div>;
};
```

#### Performance Debugging
```typescript
// Use React DevTools Profiler to identify performance issues
// Add debugging hooks for performance monitoring

const usePerformanceMonitoring = (componentName: string) => {
  useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const endTime = performance.now();
      console.log(`${componentName} render time: ${endTime - startTime}ms`);
    };
  });
};

const StockChart = ({ data }) => {
  usePerformanceMonitoring('StockChart');
  
  // Component logic
};
```

### TypeScript Debugging

#### Type Error Resolution
```typescript
// Issue: Type mismatch with API response
interface StockData {
  symbol: string;
  price: number;
  change: number;
}

// API returns string for price, but interface expects number
const processStockData = (apiResponse: any): StockData => {
  return {
    symbol: apiResponse.symbol,
    price: apiResponse.price, // Type error: string not assignable to number
    change: apiResponse.change
  };
};

// Solution: Type validation and conversion
const processStockData = (apiResponse: any): StockData => {
  return {
    symbol: apiResponse.symbol,
    price: Number(apiResponse.price), // Convert to number
    change: Number(apiResponse.change)
  };
};
```

## Backend Debugging

### Python Error Diagnosis

#### API Integration Debugging
```python
import logging
import traceback
from functools import wraps

def debug_api_call(func):
    """Decorator to debug API calls with detailed logging."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        
        try:
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            
            logging.info(f"{func.__name__} completed in {end_time - start_time:.2f}s")
            return result
            
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            raise
            
    return wrapper

@debug_api_call
async def fetch_korean_stock_data(symbol: str):
    # Korean Investment Securities API call
    pass
```

#### Database Query Debugging
```python
import time
import logging

class DatabaseQueryLogger:
    def __init__(self):
        self.queries = []
    
    def log_query(self, query: str, params: tuple = None):
        start_time = time.time()
        
        def log_completion(result_count: int):
            end_time = time.time()
            execution_time = end_time - start_time
            
            self.queries.append({
                'query': query,
                'params': params,
                'execution_time': execution_time,
                'result_count': result_count,
                'timestamp': start_time
            })
            
            if execution_time > 1.0:  # Log slow queries
                logging.warning(f"Slow query ({execution_time:.2f}s): {query}")
        
        return log_completion

# Usage
query_logger = DatabaseQueryLogger()

def get_stock_data(symbol: str):
    query = "SELECT * FROM stocks WHERE symbol = %s"
    log_completion = query_logger.log_query(query, (symbol,))
    
    result = db.execute(query, (symbol,))
    log_completion(len(result))
    
    return result
```

#### Financial Calculation Debugging
```python
def debug_financial_calculation(calculation_name: str):
    """Decorator to validate financial calculations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # Validate result is not NaN or infinite
                if isinstance(result, (int, float)):
                    if math.isnan(result) or math.isinf(result):
                        logging.error(f"Invalid calculation result in {calculation_name}: {result}")
                        raise ValueError(f"Invalid calculation result: {result}")
                
                # Log calculation for audit trail
                logging.info(f"{calculation_name} calculated: {result}")
                return result
                
            except ZeroDivisionError as e:
                logging.error(f"Division by zero in {calculation_name}: {args}, {kwargs}")
                raise
            except Exception as e:
                logging.error(f"Error in {calculation_name}: {str(e)}")
                raise
                
        return wrapper
    return decorator

@debug_financial_calculation("PE Ratio")
def calculate_pe_ratio(price: float, earnings_per_share: float) -> float:
    if earnings_per_share == 0:
        raise ValueError("Earnings per share cannot be zero")
    return price / earnings_per_share
```

## Market-Specific Debugging

### Korean Market Issues

#### Currency Formatting Debug
```python
def debug_korean_currency(amount: float) -> str:
    """Debug Korean Won formatting issues."""
    try:
        # Korean Won should not have decimal places
        if amount != int(amount):
            logging.warning(f"Korean Won amount has decimals: {amount}")
        
        # Format as Korean Won
        formatted = f"{int(amount):,}원"
        logging.debug(f"Formatted Korean amount: {amount} -> {formatted}")
        return formatted
        
    except Exception as e:
        logging.error(f"Error formatting Korean currency {amount}: {str(e)}")
        return f"{amount}원"
```

#### Korean Investment Securities API Debug
```python
async def debug_korean_api_response(endpoint: str, response: dict):
    """Debug Korean Investment Securities API responses."""
    required_fields = ['rt_cd', 'msg_cd', 'msg1']
    
    # Check for required response fields
    for field in required_fields:
        if field not in response:
            logging.error(f"Missing required field in Korean API response: {field}")
    
    # Check for error codes
    if response.get('rt_cd') != '0':
        error_msg = response.get('msg1', 'Unknown error')
        logging.error(f"Korean API error for {endpoint}: {error_msg}")
        raise APIError(f"Korean API error: {error_msg}")
    
    logging.debug(f"Korean API response for {endpoint}: {response}")
```

### US Market Issues

#### Timezone Debug
```python
import pytz
from datetime import datetime

def debug_market_hours(market_type: str):
    """Debug market hours for US market."""
    if market_type == 'us':
        eastern = pytz.timezone('US/Eastern')
        current_time = datetime.now(eastern)
        
        # Check if market is open
        market_open = current_time.replace(hour=9, minute=30, second=0)
        market_close = current_time.replace(hour=16, minute=0, second=0)
        
        is_weekday = current_time.weekday() < 5
        is_market_hours = market_open <= current_time <= market_close
        
        logging.info(f"US Market Debug - Current time: {current_time}")
        logging.info(f"Is weekday: {is_weekday}, In market hours: {is_market_hours}")
        
        return is_weekday and is_market_hours
```

## Debugging Tools and Techniques

### Logging Strategy
```python
import logging
import sys

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hts_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Create separate loggers for different components
api_logger = logging.getLogger('api')
data_logger = logging.getLogger('data')
performance_logger = logging.getLogger('performance')
```

### Error Monitoring
```typescript
// Frontend error boundary
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    
    // Send error to monitoring service
    sendErrorToMonitoring({
      error: error.toString(),
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString()
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <details>
            {this.state.error && this.state.error.toString()}
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Performance Monitoring
```python
import time
from contextlib import contextmanager

@contextmanager
def performance_monitor(operation_name: str):
    """Context manager to monitor operation performance."""
    start_time = time.time()
    start_memory = get_memory_usage()
    
    try:
        yield
    finally:
        end_time = time.time()
        end_memory = get_memory_usage()
        
        execution_time = end_time - start_time
        memory_delta = end_memory - start_memory
        
        logging.info(f"Performance - {operation_name}:")
        logging.info(f"  Execution time: {execution_time:.3f}s")
        logging.info(f"  Memory usage change: {memory_delta:.2f}MB")
        
        if execution_time > 5.0:
            logging.warning(f"Slow operation detected: {operation_name}")

# Usage
with performance_monitor("Process large dataset"):
    process_market_data(large_dataset)
```

Follow established [error handling patterns](./.github/instructions/security.instructions.md) and apply [performance optimization](./.github/instructions/performance.instructions.md) principles during debugging.