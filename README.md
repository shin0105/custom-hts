# Custom HTS (Home Trading System)

A modern web-based Home Trading System for Korean and US stock markets, built with React/TypeScript frontend and Python backend.

## Features

- **Korean Market Integration**
  - Real-time data via Korean Investment Securities (KDevelopers) OpenAPI
  - Financial statements from OPENDART API
  - Korean Won currency support
  
- **US Market Integration**
  - Market data via Yahoo Finance API
  - US company financial statements
  - USD currency support

- **HTS-like Interface**
  - Separate pages for Korean and US markets
  - Real-time stock quotes and charts
  - Financial statement analysis
  - Trading interface components

## Tech Stack

### Frontend
- React with TypeScript
- Vite for build tooling
- Modern component-based architecture
- Responsive design for desktop and mobile

### Backend
- Python with FastAPI
- UV for package management
- Pandas for data processing
- Supabase PostgreSQL for data persistence

### APIs
- Korean Investment Securities (KDevelopers) OpenAPI
- OPENDART API for Korean financial data
- Yahoo Finance for US market data

## Project Structure

```
custom-hts/
├── frontend/              # React TypeScript application
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components (Korean/US)
│   │   ├── hooks/        # Custom React hooks
│   │   ├── services/     # API service layers
│   │   ├── types/        # TypeScript type definitions
│   │   └── utils/        # Utility functions
│   ├── public/           # Static assets
│   └── package.json
│
├── backend/              # Python backend
│   ├── src/
│   │   ├── api/         # FastAPI route handlers
│   │   ├── services/    # Business logic
│   │   ├── models/      # Data models
│   │   ├── integrations/# External API integrations
│   │   └── utils/       # Utility functions
│   └── pyproject.toml
│
└── docs/                # Documentation

```

## Prerequisites

- Python 3.11+
- Node.js 18+
- UV package manager for Python
- Supabase account (free tier)

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required API keys:
- **HANTU_API_KEY**: Korean Investment Securities API key from [KDevelopers](https://apiportal.koreainvestment.com/)
- **HANTU_API_SECRET**: Korean Investment Securities API secret
- **DART_API_KEY**: OPENDART API key from [OpenDart](https://opendart.fss.or.kr/)
- **SUPABASE_URL**: Your Supabase project URL
- **SUPABASE_KEY**: Your Supabase anon key

### 2. Backend Setup

Install UV if not already installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Set up the backend:

```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

Run the backend server:

```bash
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

### 3. Frontend Setup

Install dependencies:

```bash
cd frontend
npm install
```

Run the development server:

```bash
npm run dev
```

The application will be available at http://localhost:5173

## Development

### Running Tests

Backend tests:
```bash
cd backend
uv run pytest
```

Frontend tests:
```bash
cd frontend
npm test
```

### Code Quality

The project follows strict coding guidelines. See `.github/instructions/` for details:
- TypeScript/React guidelines
- Python development standards
- Security best practices
- Performance optimization guidelines

### Building for Production

Backend:
```bash
cd backend
uv build
```

Frontend:
```bash
cd frontend
npm run build
```

## Database

The application uses Supabase PostgreSQL with the following constraints:
- 500 MB database size
- 5 GB egress
- 5 GB cached egress
- 1 GB file storage

Financial statements and frequently accessed data are cached in the database to minimize API calls and improve performance.

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation powered by FastAPI's automatic OpenAPI generation.

## Contributing

1. Follow the coding guidelines in `.github/instructions/`
2. Write tests for new features
3. Update documentation as needed
4. Submit pull requests for review

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub.

## Documentation

- [Setup Guide](docs/SETUP.md) - Detailed setup instructions
- [API Documentation](docs/API.md) - Complete API reference
- [Database Schema](database/schema.md) - Database design and tables
- [Backend README](backend/README.md) - Backend specific documentation
- [Frontend README](frontend/README.md) - Frontend specific documentation

## Project Status

This is a functional HTS (Home Trading System) application with:
- ✅ Complete backend API with FastAPI
- ✅ React TypeScript frontend with routing
- ✅ Korean market integration (KDevelopers + OPENDART)
- ✅ US market integration (Yahoo Finance)
- ✅ Database schema for data caching
- ✅ Comprehensive documentation
- ✅ Basic test coverage

Future enhancements:
- Real-time WebSocket data updates
- Advanced charting with technical indicators
- User authentication and watchlists
- Portfolio tracking
- Price alerts
- Mobile-responsive improvements
