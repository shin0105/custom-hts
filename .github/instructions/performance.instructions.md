---
applyTo: "**/*"
description: "Performance optimization guidelines for HTS application"
---

# Performance Optimization Guidelines for HTS Application

Optimize application performance to handle real-time financial data efficiently.

## Frontend Performance

### React Optimization
- Use React.memo for pure components to prevent unnecessary re-renders
- Implement useMemo for expensive calculations and data transformations
- Use useCallback for event handlers passed to child components
- Optimize dependency arrays in hooks to prevent excessive updates
- Implement code splitting and lazy loading for route-based optimization

### Data Handling
- Implement virtualization for large data tables and lists
- Use pagination for large datasets to reduce initial load time
- Implement efficient data caching strategies
- Debounce user inputs to reduce API calls
- Use proper data structures for fast lookups and filtering

### Real-time Updates
- Optimize WebSocket connection management
- Implement efficient data diffing for real-time updates
- Use throttling for high-frequency data updates
- Implement selective component updates based on data changes
- Use efficient state management for real-time data

### Bundle Optimization
- Minimize bundle size through tree shaking and dead code elimination
- Use dynamic imports for feature-based code splitting
- Optimize asset loading with proper compression and caching
- Implement service workers for offline functionality and caching
- Use CDN for static assets and third-party libraries

## Backend Performance

### Database Optimization
- Design efficient database schemas with proper indexing
- Use connection pooling for database connections
- Implement query optimization and avoid N+1 queries
- Use database-level caching where appropriate
- Optimize data archival strategies within 500MB limit

### API Performance
- Implement proper caching strategies for API responses
- Use efficient data serialization formats
- Implement pagination for large data sets
- Use async/await patterns for non-blocking operations
- Optimize external API call patterns and batching

### Data Processing
- Use pandas vectorized operations for bulk data processing
- Implement parallel processing for independent data operations
- Optimize memory usage for large dataset processing
- Use efficient data structures and algorithms
- Implement streaming for large data transfers

### Caching Strategies
- Implement multi-level caching (memory, Redis, database)
- Use appropriate cache expiration strategies
- Implement cache invalidation for real-time data
- Use cache warming for frequently accessed data
- Monitor cache hit rates and effectiveness

## Network Performance

### API Optimization
- Minimize API payload sizes through efficient data structures
- Implement request batching where possible
- Use appropriate HTTP status codes and headers
- Implement proper compression for API responses
- Use efficient authentication mechanisms

### External API Management
- Implement intelligent rate limiting and throttling
- Use connection pooling for external API calls
- Implement retry mechanisms with exponential backoff
- Cache external API responses where appropriate
- Monitor external API performance and reliability

### Real-time Data
- Optimize WebSocket message sizes and frequency
- Implement efficient data compression for real-time streams
- Use appropriate message queuing for high-volume data
- Implement client-side buffering for smooth data display
- Monitor real-time data latency and throughput

## Memory Management

### Frontend Memory
- Implement proper cleanup in useEffect hooks
- Avoid memory leaks in event listeners and timers
- Use weak references where appropriate
- Monitor component memory usage during development
- Implement efficient data structure management

### Backend Memory
- Monitor memory usage during data processing operations
- Implement proper garbage collection strategies
- Use memory-efficient data structures for large datasets
- Implement memory profiling in development environment
- Set appropriate memory limits and monitoring

## Monitoring and Optimization

### Performance Monitoring
- Implement application performance monitoring (APM)
- Monitor key performance indicators (KPIs) and metrics
- Set up alerts for performance degradation
- Track user experience metrics and page load times
- Monitor database query performance and optimization opportunities

### Profiling and Analysis
- Use browser developer tools for frontend profiling
- Implement backend performance profiling
- Analyze bundle sizes and loading performance
- Profile database query execution plans
- Use performance testing tools for load testing

### Continuous Optimization
- Implement performance testing in CI/CD pipeline
- Set performance budgets and thresholds
- Regular performance reviews and optimization cycles
- Monitor performance impact of new features
- Document performance optimization decisions and results

## Market-Specific Optimizations

### Korean Market Data
- Optimize for Korean Won currency formatting and calculations
- Handle Korean market hours and holiday schedules efficiently
- Implement efficient Korean text rendering and processing
- Optimize for Korean Investment Securities API response patterns
- Cache Korean corporate disclosure data appropriately

### US Market Data
- Optimize for multiple timezone handling
- Implement efficient US market data processing
- Handle high-frequency US market data updates
- Optimize Yahoo Finance API integration patterns
- Implement efficient currency conversion calculations

### Cross-Market Synchronization
- Optimize data synchronization between Korean and US markets
- Implement efficient market comparison features
- Handle different market state management
- Optimize portfolio calculations across markets
- Implement efficient cross-market analytics

## Resource Constraints

### Supabase Limitations
- Optimize database usage within 500MB limit
- Implement efficient data archival and cleanup
- Use file storage effectively for large datasets
- Monitor egress usage and optimization
- Implement efficient query patterns for small database

### Cost Optimization
- Optimize API call patterns to reduce external costs
- Implement efficient data storage strategies
- Monitor resource usage and costs
- Optimize deployment and hosting costs
- Implement usage-based optimization strategies