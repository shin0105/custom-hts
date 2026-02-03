<!-- Based on: https://github.com/github/awesome-copilot/blob/main/instructions/python.instructions.md -->
---
applyTo: "**/*.py"
description: "Python development guidelines for HTS backend with financial data processing"
---

# Python Development Guidelines for HTS Backend

Apply the [general coding guidelines](../copilot-instructions.md) to all Python code.

## Python Best Practices

### Code Style and Formatting
- Follow **PEP 8** style guide for Python
- Maintain proper indentation (use 4 spaces for each level)
- Ensure lines do not exceed 79 characters
- Use blank lines to separate functions, classes, and code blocks
- Place function and class docstrings immediately after the `def` or `class` keyword

### Type Hints and Documentation
- Write clear and concise comments for each function
- Ensure functions have descriptive names and include type hints
- Provide docstrings following PEP 257 conventions
- Use the `typing` module for type annotations (e.g., `List[str]`, `Dict[str, int]`)
- Break down complex functions into smaller, more manageable functions

### UV Package Management
- Use `uv` for all Python package management
- Define dependencies in `pyproject.toml` with version constraints
- Create virtual environments using `uv venv`
- Install packages using `uv add` command
- Pin exact versions for production deployments

### Financial Data Processing
- Use pandas for efficient data manipulation and analysis
- Implement proper data validation for financial data
- Handle different number formats (Korean Won, USD)
- Use appropriate data types for financial calculations (Decimal for precision)
- Cache frequently accessed data to minimize API calls

### API Integration Patterns
- Implement proper error handling for external API calls
- Use async/await for non-blocking API requests
- Implement exponential backoff for rate-limited APIs
- Store API keys in environment variables
- Validate API responses before processing

### Database Operations
- Use Supabase Python client for database operations
- Implement proper connection pooling
- Use prepared statements to prevent SQL injection
- Optimize queries for the 500MB database limit
- Implement data archiving strategies for historical data

### Error Handling and Logging
- Use structured logging with appropriate log levels
- Implement comprehensive exception handling
- Create custom exceptions for business logic errors
- Log API errors and performance metrics
- Handle network timeouts gracefully

### Testing Guidelines
- Write unit tests for all business logic functions
- Mock external API calls in tests
- Test data processing pipelines with sample data
- Include performance tests for data-heavy operations
- Use pytest fixtures for consistent test data

### Security Considerations
- Never commit API keys or sensitive credentials
- Use environment variables for all configuration
- Implement proper input validation and sanitization
- Use secure HTTP headers for API requests
- Validate and sanitize data from external APIs

## Financial API Specific Guidelines

### Korean Investment Securities (KDevelopers)
- Respect rate limits and implement proper throttling
- Handle Korean market hours and holidays
- Use appropriate authentication headers
- Parse Korean financial data formats correctly

### OPENDART Integration
- Implement caching for corporate disclosure data
- Handle large XML/JSON responses efficiently
- Respect API rate limits (up to 10,000 calls per day)
- Store processed financial statements in database

### Yahoo Finance Integration
- Use the official yfinance library
- Handle different market timezone conversions
- Implement data freshness validation
- Cache symbol lookups and historical data

## Performance Optimization
- Use pandas vectorized operations for bulk data processing
- Implement data pagination for large datasets
- Use database indexes for frequently queried fields
- Monitor memory usage for large data processing
- Profile code performance for bottleneck identification