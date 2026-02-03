# Custom HTS - Agent Skills Reference

This document provides a comprehensive overview of the Custom HTS (Home Trading System) project to help AI agents understand the project structure, capabilities, and development practices.

## Project Overview

Custom HTS is a modern web-based Home Trading System for analyzing Korean and US stock markets. It combines real-time market data, financial statement analysis, and HTS-like trading interfaces in a single application.

### Core Purpose
- Provide unified access to Korean and US stock market data
- Display real-time quotes, charts, and financial statements
- Cache financial data for efficient access within database constraints
- Offer HTS-like user interface for traders and investors

## Technology Stack

### Frontend
- **Framework**: React 18.3+ with TypeScript 5.5+
- **Build Tool**: Vite 5.4+
- **Routing**: React Router DOM 6.26+
- **State Management**: TanStack React Query 5.56+ for server state
- **Charts**: Recharts 2.12+ for data visualization
- **HTTP Client**: Axios 1.7+
- **Styling**: CSS with responsive design patterns

### Backend
- **Framework**: FastAPI 0.115+ (Python 3.11+)
- **Package Manager**: UV for Python dependency management
- **Server**: Uvicorn with async/await support
- **Data Processing**: Pandas 2.2+ for financial data analysis
- **API Client**: httpx, requests, yfinance, beautifulsoup4
- **Validation**: Pydantic 2.9+ for data validation
- **Database**: Supabase PostgreSQL client 2.10+

### Database
- **Provider**: Supabase PostgreSQL
- **Size Limit**: 500MB (free tier)
- **Storage**: 1GB file storage
- **Egress**: 5GB (with 5GB cached)

### External APIs
- **Korean Investment Securities (KDevelopers)**: Real-time Korean market data
- **OPENDART API**: Korean corporate financial statements and disclosures
- **Yahoo Finance (yfinance)**: US market data and financial statements

## Project Structure

```
custom-hts/
├── frontend/                    # React TypeScript application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Page components (Korean/US markets)
│   │   ├── hooks/              # Custom React hooks
│   │   ├── services/           # API service layers
│   │   ├── utils/              # Utility functions
│   │   └── types/              # TypeScript type definitions
│   ├── public/                 # Static assets
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript configuration
│   └── vite.config.ts          # Vite build configuration
│
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── api/               # FastAPI route handlers
│   │   │   ├── korean.py      # Korean market endpoints
│   │   │   └── us.py          # US market endpoints
│   │   ├── services/          # Business logic services
│   │   │   ├── korean_market.py
│   │   │   └── us_market.py
│   │   ├── models/            # Pydantic data models
│   │   │   ├── korean.py
│   │   │   └── us.py
│   │   ├── integrations/      # External API integrations
│   │   │   └── supabase_client.py
│   │   ├── utils/             # Utility functions
│   │   │   ├── config.py      # Configuration management
│   │   │   └── helpers.py     # Helper functions
│   │   └── main.py            # FastAPI application entry
│   ├── tests/                 # Backend test suite
│   └── pyproject.toml         # Python dependencies and config
│
├── database/                   # Database schemas and migrations
│   ├── init.sql               # Database initialization
│   └── schema.md              # Database schema documentation
│
├── docs/                       # Documentation
│   ├── API.md                 # API reference documentation
│   ├── SETUP.md               # Setup instructions
│   ├── PROJECT_SUMMARY.md     # Project overview
│   └── CONTRIBUTING.md        # Contribution guidelines
│
├── .github/                    # GitHub configuration
│   ├── copilot-instructions.md # Main development guidelines
│   ├── instructions/          # Specific coding guidelines
│   │   ├── typescript.instructions.md
│   │   ├── python.instructions.md
│   │   ├── security.instructions.md
│   │   ├── performance.instructions.md
│   │   ├── testing.instructions.md
│   │   ├── documentation.instructions.md
│   │   └── code-review.instructions.md
│   ├── agents/                # Custom agent definitions
│   │   ├── architect.agent.md
│   │   ├── debugger.agent.md
│   │   └── reviewer.agent.md
│   └── prompts/               # Reusable prompts
│       ├── code-review.prompt.md
│       ├── debug-issue.prompt.md
│       ├── generate-docs.prompt.md
│       ├── refactor-code.prompt.md
│       ├── setup-component.prompt.md
│       └── write-tests.prompt.md
│
└── tests/                     # Integration tests
```

## Key Features and Capabilities

### Korean Market Integration
- **Real-time Data**: Korean Investment Securities (KDevelopers) OpenAPI integration
- **Financial Statements**: OPENDART API for corporate disclosures
- **Currency**: Korean Won (KRW) handling and formatting
- **Market Hours**: Korean market trading hours and holiday schedules
- **Data Caching**: Efficient caching to minimize API calls

### US Market Integration
- **Market Data**: Yahoo Finance API via yfinance library
- **Financial Statements**: US company financial data
- **Currency**: US Dollar (USD) handling
- **Timezone**: US market timezone conversions
- **Symbol Lookup**: Ticker symbol search and validation

### Data Processing
- **Pandas Operations**: Vectorized data processing for performance
- **Data Validation**: Pydantic models for type safety and validation
- **Caching Strategy**: Multi-level caching (memory, database)
- **Real-time Updates**: WebSocket support for live data (planned)
- **Historical Data**: Time-series data storage and retrieval

### User Interface
- **Responsive Design**: Mobile and desktop support
- **Market Pages**: Separate pages for Korean and US markets
- **Charts**: Interactive candlestick and volume charts
- **Tables**: Sortable and filterable data tables
- **Real-time Quotes**: Live price updates (planned)

## Development Patterns

### Frontend Patterns
- **Component Architecture**: Functional components with hooks
- **Type Safety**: TypeScript strict mode enabled
- **State Management**: React Query for server state, useState/useReducer for local state
- **Performance**: React.memo, useMemo, useCallback for optimization
- **Error Handling**: Error boundaries and graceful error states
- **Code Splitting**: Dynamic imports for route-based splitting

### Backend Patterns
- **Async/Await**: Non-blocking I/O operations
- **Dependency Injection**: FastAPI dependency system
- **Error Handling**: Comprehensive exception handling with proper HTTP status codes
- **Rate Limiting**: Throttling for external API calls
- **Connection Pooling**: Efficient database connection management
- **Data Validation**: Pydantic models for request/response validation

### API Integration Patterns
- **Authentication**: Environment-based API key management
- **Rate Limiting**: Exponential backoff and retry mechanisms
- **Response Validation**: Schema validation for external APIs
- **Error Handling**: Graceful degradation on API failures
- **Caching**: Intelligent caching to reduce API calls

### Database Patterns
- **Schema Design**: Normalized schema with proper indexes
- **Data Archival**: Strategies for 500MB limit management
- **Query Optimization**: Efficient queries with proper indexes
- **Connection Management**: Supabase client with pooling
- **File Storage**: Large datasets in Supabase file storage

## Quality Assurance

### Testing Strategy
- **Unit Tests**: pytest for Python, React Testing Library for frontend
- **Integration Tests**: API endpoint testing with mocked external services
- **Test Coverage**: Minimum 80% coverage (90% for financial logic)
- **Mock Strategy**: Consistent mock data for external APIs
- **Async Testing**: Proper async/await test patterns

### Code Quality
- **Linting**: ESLint for TypeScript, flake8 for Python
- **Formatting**: Prettier for TypeScript, Black for Python
- **Type Checking**: TypeScript strict mode, mypy for Python
- **Code Review**: Peer review required before merging
- **Security Scanning**: Automated dependency vulnerability checks

### Performance Standards
- **Bundle Size**: Optimized frontend bundle with code splitting
- **API Response**: Fast response times with caching
- **Database Queries**: Optimized queries with indexes
- **Real-time Data**: Efficient WebSocket message handling
- **Memory Management**: Proper cleanup and garbage collection

### Security Standards
- **API Keys**: Environment variables, never committed
- **Input Validation**: Sanitization and validation of all inputs
- **Data Encryption**: HTTPS/TLS for all communications
- **SQL Injection**: Parameterized queries only
- **CORS**: Proper CORS configuration
- **Authentication**: Secure session management (planned)

## Configuration and Environment

### Environment Variables
```
# Korean Investment Securities API
HANTU_API_KEY=your_key
HANTU_API_SECRET=your_secret

# OPENDART API
DART_API_KEY=your_key

# Supabase
SUPABASE_URL=your_url
SUPABASE_KEY=your_key

# Application
API_V1_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Development Commands

#### Backend
```bash
cd backend
uv venv                          # Create virtual environment
source .venv/bin/activate        # Activate (Linux/Mac)
uv pip install -e .             # Install dependencies
uv run uvicorn src.main:app --reload  # Run dev server
uv run pytest                    # Run tests
black src/                       # Format code
flake8 src/                      # Lint code
```

#### Frontend
```bash
cd frontend
npm install                      # Install dependencies
npm run dev                      # Run dev server
npm run build                    # Build for production
npm run lint                     # Lint code
npm run format                   # Format code
npm test                         # Run tests
```

## Agent Guidance

### When Working on This Project

1. **Read Guidelines First**: Always review `.github/copilot-instructions.md` and relevant instruction files before making changes

2. **Follow Standards**: 
   - TypeScript: Use strict mode, proper typing, functional components
   - Python: Use type hints, async/await, Pydantic models
   - Testing: Write tests for new features, maintain coverage
   - Documentation: Update docs for significant changes

3. **Security Priority**:
   - Never commit API keys or secrets
   - Validate all external data
   - Use parameterized queries
   - Follow OWASP guidelines

4. **Performance Considerations**:
   - Optimize for 500MB database limit
   - Cache frequently accessed data
   - Use efficient data structures
   - Minimize external API calls

5. **Market-Specific Knowledge**:
   - Korean market: KRW currency, specific trading hours
   - US market: USD currency, timezone handling
   - Different data formats and APIs for each market

6. **Testing Requirements**:
   - Unit tests for business logic
   - Integration tests for API endpoints
   - Mock external API calls
   - Test error handling and edge cases

7. **Available Custom Agents**:
   - `architect`: Generate architecture plans for new features
   - `debugger`: Specialized debugging assistance
   - `reviewer`: Comprehensive code review

8. **Common Tasks**:
   - Adding new market data endpoints
   - Creating new React components
   - Implementing data caching strategies
   - Integrating new external APIs
   - Optimizing database queries

### Project Constraints

- **Database**: 500MB limit requires careful data management
- **API Limits**: Rate limiting on external APIs requires caching
- **Free Tier**: Supabase free tier has egress and storage limits
- **Real-time**: WebSocket implementation is planned but not yet complete

### Future Enhancements
- Real-time WebSocket data updates
- User authentication and authorization
- Portfolio tracking and management
- Price alerts and notifications
- Advanced technical indicators
- Mobile app development

## Getting Help

- **Documentation**: Check `docs/` directory for detailed guides
- **API Reference**: Visit `/docs` endpoint when backend is running
- **Issues**: GitHub issues for bug reports and feature requests
- **Guidelines**: `.github/instructions/` for coding standards

## Quick Reference

### Key Files to Understand
1. `.github/copilot-instructions.md` - Main development guidelines
2. `backend/src/main.py` - FastAPI application entry point
3. `backend/src/api/` - API endpoint definitions
4. `backend/src/services/` - Business logic for market data
5. `frontend/src/pages/` - Main application pages
6. `database/schema.md` - Database structure

### Important Concepts
- **Market Separation**: Korean and US markets have separate code paths
- **Data Caching**: Essential for performance and API limit management
- **Type Safety**: TypeScript and Pydantic ensure data integrity
- **Async Operations**: Non-blocking I/O throughout the stack
- **Component Reusability**: Shared components between market pages

This skills reference should help agents quickly understand the project structure, make informed decisions, and contribute effectively to the Custom HTS application.
