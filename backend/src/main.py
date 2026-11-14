"""Main FastAPI application for Custom HTS backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .utils.config import settings
from .api import korean, us, financial_statements

# Validate settings on startup
settings.validate()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for Custom Home Trading System",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(korean.router, prefix=settings.API_V1_PREFIX)
app.include_router(us.router, prefix=settings.API_V1_PREFIX)
app.include_router(
    financial_statements.router,
    prefix=f"{settings.API_V1_PREFIX}/financials",
    tags=["Financial Statements"],
)


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
