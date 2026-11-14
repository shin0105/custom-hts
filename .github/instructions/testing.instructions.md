---
applyTo: "**/*.test.{js,ts,tsx},**/*.spec.{js,ts,tsx}"
description: "Testing standards and practices for HTS application"
---

# Testing Guidelines for HTS Application

Apply comprehensive testing practices to ensure reliability of financial data processing and user interface functionality.

## Testing Strategy

### Test Pyramid
- **Unit Tests**: 70% - Test individual functions and components
- **Integration Tests**: 20% - Test component interactions and API integrations
- **End-to-End Tests**: 10% - Test complete user workflows

### Testing Scope
- All financial data processing functions
- API integration endpoints
- React component rendering and interactions
- Data validation and error handling
- User interface workflows

## Frontend Testing (React/TypeScript)

### Component Testing
- Use React Testing Library for component tests
- Test component behavior, not implementation details
- Focus on user interactions and rendered output
- Mock external dependencies and API calls
- Test accessibility features and keyboard navigation

### Test Structure
- Use describe blocks to group related tests
- Write clear, descriptive test names
- Follow Arrange-Act-Assert pattern
- Keep tests isolated and independent
- Use setup and cleanup hooks appropriately

### Mock Strategy
- Mock API calls with consistent response shapes
- Mock expensive operations and external dependencies
- Use MSW (Mock Service Worker) for API mocking
- Create reusable mock data for financial information
- Mock real-time data updates and WebSocket connections

### Async Testing
- Use proper async/await patterns in tests
- Test loading states and data fetching
- Test error states and retry mechanisms
- Verify proper cleanup of async operations
- Handle timeout scenarios appropriately

## Backend Testing (Python)

### Unit Testing
- Use pytest as the primary testing framework
- Test all data processing functions thoroughly
- Test API endpoint handlers and business logic
- Mock external API calls to Korean Investment Securities and OPENDART
- Test database operations with test database

### Data Testing
- Validate financial data parsing and processing
- Test number formatting and currency conversions
- Test data validation rules and constraints
- Verify data integrity after transformations
- Test edge cases with malformed or missing data

### API Testing
- Test HTTP request/response cycles
- Validate request authentication and headers
- Test rate limiting and error handling
- Verify proper status codes and error messages
- Test API response serialization

### Database Testing
- Use test database for integration tests
- Test database migrations and schema changes
- Verify proper data relationships and constraints
- Test query performance and optimization
- Test data archival and cleanup procedures

## Integration Testing

### API Integration
- Test complete data flow from external APIs to database
- Verify proper error handling for API failures
- Test data synchronization between Korean and US markets
- Test real-time data updates and WebSocket connections
- Verify proper caching mechanisms

### Frontend-Backend Integration
- Test API calls from React components
- Verify proper error handling and user feedback
- Test data loading states and user interactions
- Test form submissions and data persistence
- Verify proper authentication and authorization

## Test Data Management

### Financial Test Data
- Create realistic but anonymized financial data
- Use consistent data formats for Korean and US markets
- Include edge cases and boundary conditions
- Maintain test data versions for different scenarios
- Document test data sources and assumptions

### Mock Data Strategy
- Create reusable mock factories for different data types
- Use consistent naming conventions for mock data
- Include both valid and invalid data scenarios
- Mock different market conditions and states
- Version control test data and mock responses

## Performance Testing

### Load Testing
- Test API endpoints under realistic load
- Verify database query performance
- Test concurrent user scenarios
- Monitor memory usage during data processing
- Test real-time data update performance

### Frontend Performance
- Test component rendering performance
- Measure bundle size and loading times
- Test data table performance with large datasets
- Verify proper virtualization for large lists
- Test chart rendering performance

## Security Testing

### Data Validation Testing
- Test input validation and sanitization
- Verify proper handling of malicious input
- Test API authentication mechanisms
- Verify proper error message handling
- Test for common security vulnerabilities

### API Security Testing
- Test API key management and rotation
- Verify proper request authentication
- Test for injection vulnerabilities
- Verify proper data encryption in transit
- Test rate limiting and abuse prevention

## Test Organization

### File Structure
- **Backend tests**: Place all Python tests in `backend/tests/` directory
- **Frontend tests**: Place all TypeScript/React tests in `frontend/src/` alongside source files
- **Test results**: Live API tests write output to `backend/tests/test-results/` (gitignored — it can contain account data; never commit it)
- Use `.test.ts` for frontend unit tests
- Use `.integration.test.ts` for frontend integration tests
- Use `test_*.py` for Python backend tests
- Create shared test utilities and helpers in the tests directory
- Organize mock data in dedicated directories

### Test Naming
- Use descriptive test names that explain the scenario
- Include setup, action, and expected result
- Group related tests in describe blocks
- Use consistent naming patterns across tests
- Include market-specific context in test names
- Python tests: `test_<feature>.py` or `test_<component>.py`
- Frontend tests: `<Component>.test.tsx` or `<feature>.test.ts`

## Continuous Testing

### Pre-commit Testing
- Run unit tests before code commits
- Include linting and type checking
- Run security scans on dependencies
- Validate test coverage thresholds
- Check for test file naming conventions

### CI/CD Testing
- Run full test suite on pull requests
- Include integration tests in CI pipeline
- Run performance tests on staging environment
- Generate test coverage reports
- Fail builds on test failures or coverage drops

## Test Coverage

### Coverage Requirements
- Maintain minimum 80% code coverage
- Require 90% coverage for financial data processing
- Ensure 100% coverage for critical security functions
- Track coverage trends over time
- Generate coverage reports for code reviews

### Coverage Exclusions
- Exclude configuration files and build scripts
- Exclude test files from coverage calculations
- Exclude generated code and type definitions
- Document reasons for coverage exclusions
- Review exclusions regularly