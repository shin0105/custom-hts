# Custom HTS - Project Summary

## Project Overview

Custom HTS is a full-stack Home Trading System web application that provides access to both Korean and US stock markets with real-time data and financial analysis capabilities.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **Package Manager**: UV
- **Database**: Supabase PostgreSQL
- **External APIs**:
  - Korean Investment Securities (KDevelopers) OpenAPI
  - OPENDART API
  - Yahoo Finance (via yfinance)
- **Data Processing**: Pandas
- **Testing**: pytest

### Frontend
- **Framework**: React 18
- **Language**: TypeScript (strict mode)
- **Build Tool**: Vite
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Styling**: CSS-in-JS (inline styles)

## Project Structure

```
custom-hts/
├── backend/                # Python FastAPI backend
│   ├── src/
│   │   ├── api/           # REST API endpoints
│   │   ├── integrations/  # External API clients
│   │   ├── models/        # Pydantic data models
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utility functions
│   └── tests/             # Backend tests
├── frontend/              # React TypeScript frontend
│   └── src/
│       ├── components/    # Reusable UI components
│       ├── pages/         # Page components
│       ├── services/      # API service layer
│       ├── types/         # TypeScript types
│       └── utils/         # Utility functions
├── database/              # Database schema and migrations
├── docs/                  # Documentation
└── .github/               # GitHub configuration and instructions
```

## Key Features

### Implemented ✅

1. **Korean Market Support**
   - Real-time stock quotes via KDevelopers API
   - Financial statements from OPENDART
   - Korean Won currency formatting
   - Korean company data

2. **US Market Support**
   - Real-time stock quotes via Yahoo Finance
   - Historical financial statements
   - USD currency formatting
   - Market cap data

3. **Data Management**
   - PostgreSQL database for caching
   - Optimized for 500MB storage limit
   - Automatic cache management
   - Efficient query patterns

4. **User Interface**
   - Separate pages for Korean and US markets
   - Stock search functionality
   - Real-time quote display
   - Financial statement tables
   - Responsive design
   - Clean, modern UI

5. **Developer Experience**
   - Type-safe codebase (TypeScript + Python type hints)
   - Comprehensive documentation
   - Test infrastructure
   - Development guidelines
   - API documentation

## File Statistics

- **Backend**: 19 Python source files
- **Frontend**: 12 TypeScript/TSX files
- **Total Documentation**: 8 markdown files
- **Test Files**: 4 test suites

## API Endpoints

### Korean Market
- `GET /api/korean/quote/{symbol}` - Real-time quote
- `GET /api/korean/financials/{symbol}` - Financial statements
- `GET /api/korean/health` - Health check

### US Market
- `GET /api/us/quote/{symbol}` - Real-time quote
- `GET /api/us/financials/{symbol}` - Financial statements
- `GET /api/us/health` - Health check

## Database Schema

### Tables
- `korean_financials` - Korean company financial data
- `us_financials` - US company financial data

Both tables include:
- Company identification (symbol, name)
- Financial metrics (revenue, income, assets, etc.)
- Timestamps for cache management
- Proper indexes for performance

## Documentation

1. **README.md** - Project overview and quick start
2. **docs/SETUP.md** - Detailed setup instructions
3. **docs/API.md** - Complete API reference
4. **docs/CONTRIBUTING.md** - Contribution guidelines
5. **database/schema.md** - Database design
6. **backend/README.md** - Backend documentation
7. **frontend/README.md** - Frontend documentation

## Testing

### Backend Tests
- Configuration management
- Data model validation
- Utility function tests
- Integration test structure

### Test Coverage
- Unit tests for core functionality
- Model validation
- Helper functions
- Configuration validation

## Development Guidelines

The project follows strict coding standards defined in `.github/instructions/`:

1. **Python Standards**
   - PEP 8 compliance
   - Type hints required
   - Comprehensive docstrings
   - UV for package management

2. **TypeScript Standards**
   - Strict mode enabled
   - Explicit typing required
   - Functional components
   - React best practices

3. **Security**
   - API keys in environment variables
   - Input validation
   - Secure data handling
   - CORS configuration

4. **Performance**
   - Database caching
   - Optimized queries
   - React optimization patterns
   - Bundle size management

## Future Enhancements

### High Priority
- Real-time WebSocket updates
- User authentication
- Advanced charting (candlesticks, technical indicators)
- Portfolio tracking

### Medium Priority
- Dark mode
- Mobile app version
- Price alerts
- Market news integration
- Comparison tools

### Low Priority
- Social features
- Trading simulation
- Advanced analytics
- Export to Excel/CSV

## Configuration

### Environment Variables Required
```env
HANTU_API_KEY          # Korean Investment API key
HANTU_API_SECRET       # Korean Investment API secret
DART_API_KEY           # OPENDART API key
SUPABASE_URL          # Supabase project URL
SUPABASE_KEY          # Supabase anon key
```

### Ports
- Backend: 8000
- Frontend: 5173

## Quick Start

```bash
# Backend
cd backend
uv venv && source .venv/bin/activate
uv pip install -e .
uv run uvicorn src.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

## Resources

- **Korean Investment**: https://apiportal.koreainvestment.com/
- **OPENDART**: https://opendart.fss.or.kr/
- **Supabase**: https://supabase.com/
- **Yahoo Finance**: https://github.com/ranaroussi/yfinance

## Project Status

**Status**: ✅ Complete and functional

The project includes:
- Complete backend implementation with all integrations
- Full frontend with Korean and US market pages
- Database schema and migration scripts
- Comprehensive documentation
- Test infrastructure
- Development guidelines

Ready for:
- Local development
- API testing
- Feature additions
- Deployment preparation

## License

MIT License - See LICENSE file for details

## Contributors

- Initial Development: [shin0105](https://github.com/shin0105)

## Acknowledgments

- Korean Investment Securities for API access
- OPENDART for financial data
- Yahoo Finance for US market data
- Supabase for database hosting

---

**Last Updated**: 2024-02-03
**Version**: 0.1.0
