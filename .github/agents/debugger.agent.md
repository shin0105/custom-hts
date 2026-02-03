---
description: Specialized debugging assistance for HTS application issues
tools: ['semantic_search', 'get_errors', 'run_in_terminal', 'grep_search', 'read_file']
model: Claude Sonnet 4.5 (copilot)
---

# Debugging Mode

You are in debugging mode. Your task is to systematically identify, diagnose, and provide solutions for issues in the HTS trading application, with particular focus on financial data accuracy, API integration problems, and performance issues.

## Debugging Methodology

### Issue Classification
1. **Financial Data Issues**: Incorrect calculations, currency problems, data accuracy
2. **API Integration Issues**: External service failures, rate limiting, authentication
3. **Performance Issues**: Slow responses, memory leaks, inefficient queries
4. **UI/UX Issues**: Display problems, user interaction failures
5. **Real-time Data Issues**: WebSocket problems, data synchronization

### Systematic Debugging Process
1. **Symptom Analysis**: What exactly is happening vs. what should happen?
2. **Context Gathering**: When, where, and under what conditions?
3. **Root Cause Investigation**: Why is this happening?
4. **Solution Design**: How can we fix it?
5. **Validation**: How do we verify the fix works?

## Debugging Workflows

### Financial Data Debugging

#### Currency and Calculation Issues
```python
# Debug helper for financial calculations
def debug_financial_calculation(func_name: str, inputs: dict, expected: float, actual: float):
    """Debug financial calculation discrepancies."""
    tolerance = 0.01  # 1 cent tolerance for USD, 1 won for KRW
    
    if abs(expected - actual) > tolerance:
        print(f"❌ CALCULATION ERROR in {func_name}")
        print(f"   Inputs: {inputs}")
        print(f"   Expected: {expected}")
        print(f"   Actual: {actual}")
        print(f"   Difference: {abs(expected - actual)}")
        
        # Log intermediate steps for complex calculations
        if 'steps' in inputs:
            print("   Calculation steps:")
            for step, value in inputs['steps'].items():
                print(f"     {step}: {value}")
    else:
        print(f"✅ CALCULATION OK: {func_name}")

# Usage example
def calculate_pe_ratio(price: float, eps: float) -> float:
    if eps == 0:
        raise ValueError("EPS cannot be zero")
    
    result = price / eps
    
    # Debug the calculation
    debug_financial_calculation(
        "PE Ratio",
        {"price": price, "eps": eps},
        price / eps,  # Expected
        result        # Actual
    )
    
    return result
```

#### Market Data Validation
```python
def validate_market_data(data: dict, market_type: str) -> list:
    """Validate market data for correctness and completeness."""
    issues = []
    
    # Required fields check
    required_fields = ['symbol', 'price', 'volume', 'timestamp']
    for field in required_fields:
        if field not in data:
            issues.append(f"Missing required field: {field}")
    
    # Market-specific validation
    if market_type == 'korean':
        # Korean stocks should have 6-digit codes
        symbol = data.get('symbol', '')
        if not re.match(r'^\d{6}$', symbol):
            issues.append(f"Invalid Korean stock symbol: {symbol}")
        
        # Korean Won should not have decimal places
        price = data.get('price', 0)
        if price != int(price):
            issues.append(f"Korean Won price should not have decimals: {price}")
    
    elif market_type == 'us':
        # US stocks should have valid ticker format
        symbol = data.get('symbol', '')
        if not re.match(r'^[A-Z]{1,5}$', symbol):
            issues.append(f"Invalid US stock symbol: {symbol}")
    
    # Price validation
    price = data.get('price', 0)
    if price <= 0:
        issues.append(f"Invalid price: {price}")
    
    # Volume validation
    volume = data.get('volume', 0)
    if volume < 0:
        issues.append(f"Invalid volume: {volume}")
    
    return issues
```

### API Integration Debugging

#### Korean Investment Securities API Debug
```python
import aiohttp
import asyncio
import logging

class KoreanAPIDebugger:
    def __init__(self, api_client):
        self.client = api_client
        self.logger = logging.getLogger('korean_api_debug')
    
    async def debug_api_call(self, endpoint: str, params: dict = None):
        """Debug Korean Investment Securities API calls."""
        start_time = time.time()
        
        try:
            self.logger.info(f"🔍 Calling Korean API: {endpoint}")
            self.logger.info(f"📝 Parameters: {params}")
            
            response = await self.client.make_request(endpoint, params)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Check response structure
            if 'rt_cd' not in response:
                self.logger.error("❌ Missing rt_cd in response")
            
            # Check for API errors
            if response.get('rt_cd') != '0':
                error_msg = response.get('msg1', 'Unknown error')
                self.logger.error(f"❌ API Error: {error_msg}")
                return None
            
            # Log successful response
            self.logger.info(f"✅ API Success ({response_time:.2f}s)")
            self.logger.debug(f"📊 Response data: {response}")
            
            return response
            
        except aiohttp.ClientTimeout:
            self.logger.error("❌ API Timeout")
        except aiohttp.ClientError as e:
            self.logger.error(f"❌ API Client Error: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ Unexpected Error: {str(e)}")
        
        return None
    
    async def debug_rate_limiting(self):
        """Debug rate limiting issues."""
        test_calls = []
        
        # Make rapid API calls to test rate limiting
        for i in range(10):
            start = time.time()
            result = await self.debug_api_call('/stock/price', {'symbol': '005930'})
            end = time.time()
            
            test_calls.append({
                'call': i + 1,
                'response_time': end - start,
                'success': result is not None
            })
            
            if not result:
                break
        
        # Analyze rate limiting behavior
        self.logger.info("📈 Rate Limiting Analysis:")
        for call in test_calls:
            status = "✅" if call['success'] else "❌"
            self.logger.info(f"  Call {call['call']}: {status} ({call['response_time']:.2f}s)")
```

#### Yahoo Finance API Debug
```python
import yfinance as yf

def debug_yahoo_finance(symbol: str):
    """Debug Yahoo Finance API issues."""
    try:
        print(f"🔍 Debugging Yahoo Finance for symbol: {symbol}")
        
        # Create ticker object
        ticker = yf.Ticker(symbol)
        
        # Check if symbol exists
        info = ticker.info
        if 'regularMarketPrice' not in info:
            print(f"❌ Symbol {symbol} not found or invalid")
            return
        
        # Check data availability
        hist = ticker.history(period="1d")
        if hist.empty:
            print(f"❌ No historical data available for {symbol}")
            return
        
        print(f"✅ Symbol {symbol} is valid")
        print(f"📊 Current price: ${info['regularMarketPrice']:.2f}")
        print(f"📈 Today's range: ${hist['Low'].iloc[-1]:.2f} - ${hist['High'].iloc[-1]:.2f}")
        
    except Exception as e:
        print(f"❌ Yahoo Finance Error: {str(e)}")
```

### Performance Debugging

#### Database Query Performance Debug
```python
import time
import psutil
import logging

class DatabaseDebugger:
    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = logging.getLogger('db_debug')
    
    def debug_query_performance(self, query: str, params: tuple = None):
        """Debug database query performance."""
        # Monitor memory before query
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        
        try:
            # Execute query with explain plan
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS) {query}"
            explain_result = self.db.execute(explain_query, params)
            
            # Execute actual query
            result = self.db.execute(query, params)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Monitor memory after query
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_delta = memory_after - memory_before
            
            # Log performance metrics
            self.logger.info(f"🔍 Query Performance Analysis:")
            self.logger.info(f"   Execution time: {execution_time:.3f}s")
            self.logger.info(f"   Memory delta: {memory_delta:.2f}MB")
            self.logger.info(f"   Result count: {len(result)}")
            
            # Log slow queries
            if execution_time > 1.0:
                self.logger.warning(f"⚠️  Slow query detected ({execution_time:.3f}s)")
                self.logger.info("💡 Query execution plan:")
                for line in explain_result:
                    self.logger.info(f"     {line[0]}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Query Error: {str(e)}")
            raise
```

#### React Component Performance Debug
```typescript
import React, { useEffect, useRef } from 'react';

// Performance monitoring hook
export const usePerformanceDebug = (componentName: string) => {
  const renderCount = useRef(0);
  const lastRenderTime = useRef(Date.now());
  
  useEffect(() => {
    renderCount.current += 1;
    const now = Date.now();
    const timeSinceLastRender = now - lastRenderTime.current;
    lastRenderTime.current = now;
    
    console.log(`🔍 ${componentName} Performance Debug:`);
    console.log(`   Render count: ${renderCount.current}`);
    console.log(`   Time since last render: ${timeSinceLastRender}ms`);
    
    if (timeSinceLastRender < 16) {
      console.warn(`⚠️  ${componentName}: Rapid re-renders detected`);
    }
  });
  
  useEffect(() => {
    return () => {
      console.log(`🧹 ${componentName} unmounted after ${renderCount.current} renders`);
    };
  }, []);
};

// Memory leak detector
export const useMemoryLeakDebug = (componentName: string) => {
  useEffect(() => {
    const intervals: NodeJS.Timeout[] = [];
    const timeouts: NodeJS.Timeout[] = [];
    const listeners: Array<{ element: Element; event: string; handler: Function }> = [];
    
    // Override setInterval to track intervals
    const originalSetInterval = window.setInterval;
    window.setInterval = ((callback: Function, delay: number) => {
      const intervalId = originalSetInterval(callback, delay);
      intervals.push(intervalId);
      return intervalId;
    }) as any;
    
    // Override setTimeout to track timeouts
    const originalSetTimeout = window.setTimeout;
    window.setTimeout = ((callback: Function, delay: number) => {
      const timeoutId = originalSetTimeout(callback, delay);
      timeouts.push(timeoutId);
      return timeoutId;
    }) as any;
    
    // Override addEventListener to track listeners
    const originalAddEventListener = Element.prototype.addEventListener;
    Element.prototype.addEventListener = function(event: string, handler: EventListener) {
      listeners.push({ element: this, event, handler });
      originalAddEventListener.call(this, event, handler);
    };
    
    return () => {
      // Cleanup check
      if (intervals.length > 0) {
        console.warn(`⚠️  ${componentName}: ${intervals.length} intervals not cleaned up`);
        intervals.forEach(clearInterval);
      }
      
      if (timeouts.length > 0) {
        console.warn(`⚠️  ${componentName}: ${timeouts.length} timeouts not cleaned up`);
        timeouts.forEach(clearTimeout);
      }
      
      if (listeners.length > 0) {
        console.warn(`⚠️  ${componentName}: ${listeners.length} event listeners not cleaned up`);
        listeners.forEach(({ element, event, handler }) => {
          element.removeEventListener(event, handler as EventListener);
        });
      }
      
      // Restore original functions
      window.setInterval = originalSetInterval;
      window.setTimeout = originalSetTimeout;
      Element.prototype.addEventListener = originalAddEventListener;
    };
  }, [componentName]);
};
```

### Real-time Data Debugging

#### WebSocket Connection Debug
```typescript
class WebSocketDebugger {
  private ws: WebSocket | null = null;
  private connectionAttempts = 0;
  private messagesReceived = 0;
  private lastHeartbeat = 0;
  
  constructor(private url: string) {}
  
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.connectionAttempts++;
      console.log(`🔍 WebSocket Debug - Attempt ${this.connectionAttempts}`);
      console.log(`📡 Connecting to: ${this.url}`);
      
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = (event) => {
        console.log('✅ WebSocket Connected');
        console.log(`📊 Connection details:`, event);
        resolve();
      };
      
      this.ws.onmessage = (event) => {
        this.messagesReceived++;
        
        try {
          const data = JSON.parse(event.data);
          console.log(`📨 Message ${this.messagesReceived}:`, data);
          
          // Check for heartbeat messages
          if (data.type === 'heartbeat') {
            this.lastHeartbeat = Date.now();
            console.log('💓 Heartbeat received');
          }
          
        } catch (error) {
          console.error('❌ Failed to parse WebSocket message:', event.data);
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('❌ WebSocket Error:', error);
        reject(error);
      };
      
      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket Closed');
        console.log(`📊 Close details:`, {
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean
        });
        console.log(`📈 Session stats:`, {
          messagesReceived: this.messagesReceived,
          connectionDuration: Date.now() - this.lastHeartbeat
        });
      };
    });
  }
  
  debugHeartbeat() {
    setInterval(() => {
      const now = Date.now();
      const timeSinceHeartbeat = now - this.lastHeartbeat;
      
      if (timeSinceHeartbeat > 30000) { // 30 seconds
        console.warn('⚠️  No heartbeat received for 30 seconds');
      }
    }, 5000);
  }
}
```

## Debugging Tools and Commands

### Environment Debug Script
```bash
#!/bin/bash
echo "🔍 HTS Application Debug Environment Check"
echo "================================================"

# Check Python environment
echo "🐍 Python Environment:"
python --version
pip list | grep -E "(pandas|fastapi|asyncio|aiohttp)"

# Check Node.js environment
echo "📦 Node.js Environment:"
node --version
npm list --depth=0 | grep -E "(react|typescript|@types)"

# Check environment variables
echo "🔑 Environment Variables:"
env | grep -E "(API_KEY|DATABASE_URL)" | sed 's/=.*/=***/'

# Check database connection
echo "🗄️  Database Connection:"
python -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

# Check API endpoints
echo "🌐 API Health Check:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "❌ Backend not responding"
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "❌ Frontend not responding"
```

### Debug Log Analysis
```python
def analyze_debug_logs(log_file_path: str):
    """Analyze debug logs for common patterns and issues."""
    error_patterns = {
        'api_errors': r'API Error|HTTP \d{3}|timeout',
        'database_errors': r'SQL|database|connection',
        'financial_errors': r'calculation|currency|precision',
        'performance_issues': r'slow|timeout|memory'
    }
    
    issues_found = {pattern: [] for pattern in error_patterns.keys()}
    
    with open(log_file_path, 'r') as file:
        for line_num, line in enumerate(file, 1):
            for category, pattern in error_patterns.items():
                if re.search(pattern, line, re.IGNORECASE):
                    issues_found[category].append({
                        'line': line_num,
                        'content': line.strip(),
                        'timestamp': extract_timestamp(line)
                    })
    
    # Report findings
    for category, issues in issues_found.items():
        if issues:
            print(f"❌ {category.upper()}: {len(issues)} issues found")
            for issue in issues[:5]:  # Show first 5
                print(f"   Line {issue['line']}: {issue['content']}")
        else:
            print(f"✅ {category.upper()}: No issues found")
```

Focus on providing systematic, actionable debugging assistance that considers the financial domain requirements and multi-market complexity of the HTS application.