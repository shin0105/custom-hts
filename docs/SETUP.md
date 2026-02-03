# Setup Guide for Custom HTS

This guide will help you set up and run the Custom HTS application on your local machine.

## Prerequisites

Before starting, ensure you have the following installed:

1. **Python 3.11 or higher**
   ```bash
   python --version
   ```

2. **Node.js 18 or higher**
   ```bash
   node --version
   ```

3. **UV Package Manager** (for Python)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

4. **Git**
   ```bash
   git --version
   ```

## Getting API Keys

You'll need to obtain API keys from the following services:

### 1. Korean Investment Securities (KDevelopers)

1. Visit [KDevelopers API Portal](https://apiportal.koreainvestment.com/)
2. Sign up for an account
3. Create an application to get:
   - API Key (App Key)
   - API Secret (App Secret)

### 2. OPENDART

1. Visit [OPENDART](https://opendart.fss.or.kr/)
2. Sign up for an account
3. Request an API key (인증키 신청)
4. Wait for approval (usually instant)

### 3. Supabase

1. Visit [Supabase](https://supabase.com/)
2. Create a free account
3. Create a new project
4. Get your project URL and anon key from Project Settings → API

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/shin0105/custom-hts.git
cd custom-hts
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your API keys:

```env
# Korean Investment Securities
HANTU_API_KEY=your_hantu_api_key_here
HANTU_API_SECRET=your_hantu_api_secret_here

# OPENDART
DART_API_KEY=your_dart_api_key_here

# Supabase
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

### 3. Set Up the Database

1. Log in to your Supabase dashboard
2. Go to SQL Editor
3. Run the SQL script from `database/init.sql`
4. Verify tables are created in Table Editor

### 4. Set Up the Backend

Navigate to the backend directory and install dependencies:

```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

For development dependencies (tests, linting):

```bash
uv pip install -e ".[dev]"
```

### 5. Set Up the Frontend

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
npm install
```

## Running the Application

### Start the Backend Server

In the backend directory with activated virtual environment:

```bash
cd backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Start the Frontend Server

In a new terminal, from the frontend directory:

```bash
cd frontend
npm run dev
```

The frontend will be available at:
- Application: http://localhost:5173

## Testing the Setup

### Test the Backend

1. Visit http://localhost:8000/docs
2. Try the `/health` endpoint - it should return `{"status": "healthy"}`
3. Try the `/api/us/quote/AAPL` endpoint to get Apple stock data

### Test the Frontend

1. Visit http://localhost:5173
2. Click on "US Market"
3. Search for "AAPL" (Apple)
4. You should see real-time stock data

## Running Tests

### Backend Tests

```bash
cd backend
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=src --cov-report=html
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Troubleshooting

### Backend Issues

**Problem**: "Module not found" errors

**Solution**: Ensure you're in the virtual environment and all dependencies are installed:
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e .
```

**Problem**: "API key not configured" warnings

**Solution**: Check your `.env` file is in the project root and contains valid API keys.

**Problem**: Database connection errors

**Solution**: Verify your Supabase credentials and that the database tables are created.

### Frontend Issues

**Problem**: "Cannot connect to backend"

**Solution**: Ensure the backend is running on port 8000.

**Problem**: CORS errors

**Solution**: Check that the backend CORS settings include your frontend URL.

**Problem**: Module not found

**Solution**: Delete `node_modules` and reinstall:
```bash
rm -rf node_modules
npm install
```

## Development Tips

### Code Quality

Format Python code:
```bash
cd backend
uv run black src tests
```

Lint Python code:
```bash
uv run flake8 src tests
```

Format TypeScript code:
```bash
cd frontend
npm run format
```

### Watching for Changes

Both servers support hot reload:
- Backend: Automatically reloads when Python files change
- Frontend: Automatically rebuilds when React/TS files change

## Production Deployment

For production deployment, refer to:
- [Backend Deployment Guide](../backend/README.md)
- [Frontend Deployment Guide](../frontend/README.md)

## Getting Help

- Check the [API Documentation](../docs/API.md)
- Review the [Database Schema](../database/schema.md)
- Open an issue on GitHub

## Next Steps

After successfully setting up the application:

1. Explore different stock symbols
2. Check financial statements
3. Compare Korean and US markets
4. Customize the UI to your preferences

Enjoy using Custom HTS! 🚀
