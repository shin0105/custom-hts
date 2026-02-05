# Custom HTS Application Development Guidelines

This repository contains a Home Trading System (HTS) web application built with React/TypeScript frontend and Python backend for Korean and US stock market data analysis.

## Project Architecture

### Frontend (React + TypeScript)
- Modern React application with TypeScript
- Separate pages for Korean and US markets
- HTS-like trading interface and data visualization
- Component-based architecture for maintainability

### Backend (Python)
- Python backend using UV package management
- Korean Investment Securities (KDevelopers) OpenAPI integration
- OPENDART API for Korean firm financial statements  
- Yahoo Finance for US firm financial statements
- Pandas for data processing and analysis
- Supabase PostgreSQL for data persistence

### Database (Supabase PostgreSQL)
- Financial statements storage
- Stock data caching
- User preferences and watchlists
- Efficient storage within 500MB limit

## Development Principles

### Code Quality
- Write clean, maintainable, and well-documented code
- Use TypeScript strict mode for type safety
- Follow functional programming patterns where appropriate
- Implement proper error handling and data validation

### Performance
- Optimize API calls and database queries
- Implement data caching strategies
- Use React optimization patterns (useMemo, useCallback)
- Minimize bundle size and loading times

### Security
- Secure API key management using environment variables
- Implement proper authentication and authorization
- Validate all external API responses
- Follow OWASP security guidelines

### Testing
- Write comprehensive unit tests for components and functions
- Include integration tests for API endpoints
- Test data processing pipelines thoroughly
- Mock external API calls in tests
- **Backend tests**: Place in `backend/tests/` directory
- **Frontend tests**: Place alongside source files in `frontend/src/`
- **Test results**: Store in `docs/reports/test-results/` directory
- **Test reports**: Document in `docs/reports/` directory

### Reports
- All test reports to be stored in the `docs/reports/` directory
- Test result data files to be stored in `docs/reports/test-results/` directory
- All code implementation to be documented in the `docs/implementations/` directory
- Must include issue number prefix in name (e.g., `IMPL_1_*.md`, `REP_1_*.md`, `TEST_1_*.md`)

## File Organization

```
custom-hts/
├── frontend/          # React TypeScript application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components (Korean/US/Home)
│   │   ├── services/      # API service layers
│   │   ├── utils/         # Utility functions
│   │   └── types/         # TypeScript type definitions
├── backend/           # Python backend
│   ├── src/
│   │   ├── api/           # API route handlers
│   │   ├── services/      # Business logic services
│   │   ├── models/        # Data models and schemas
│   │   ├── utils/         # Utility functions
│   │   └── integrations/  # External API integrations
│   └── tests/         # Backend test suite
├── database/          # Database schemas and migrations
├── docs/              # Documentation
│   ├── implementations/ # Implementation guides
│   └── reports/       # Test reports and analysis
│       └── test-results/ # Test result data files
└── .github/           # GitHub configuration
    └── instructions/  # Coding guidelines
```

## API Integration Guidelines

### Korean Investment Securities (KDevelopers)
- Use proper authentication tokens and rate limiting
- Handle Korean market trading hours and holidays
- Process Korean Won currency data correctly

### OPENDART API
- Implement proper rate limiting and caching
- Handle Korean financial statement formats
- Parse corporate disclosure data efficiently

### Yahoo Finance
- Use yfinance library for reliable US market data
- Handle different timezone considerations
- Cache frequently accessed data

### Supabase Integration
- Use connection pooling for database efficiency
- Implement proper data relationships
- Utilize file storage for large datasets when needed

## Development Workflow

1. **Feature Development**: Use feature branches with descriptive names
2. **Code Review**: All changes require review before merging
3. **Testing**: Run all tests before committing changes
4. **Documentation**: Update documentation for new features
5. **Deployment**: Use environment-specific configurations

## Getting Started

1. Set up Python environment with UV
2. Configure environment variables for API keys
3. Set up Supabase database connection
4. Install frontend dependencies
5. Run development servers for both frontend and backend

Refer to specific instruction files in [.github/instructions/](.github/instructions/) for detailed coding guidelines.