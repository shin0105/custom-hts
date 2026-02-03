"""Tests for configuration management."""

from src.utils.config import Settings


def test_settings_has_required_attributes() -> None:
    """Test that Settings has all required attributes."""
    settings = Settings()
    
    # API keys (may be empty in test environment)
    assert hasattr(settings, "HANTU_API_KEY")
    assert hasattr(settings, "HANTU_API_SECRET")
    assert hasattr(settings, "DART_API_KEY")
    assert hasattr(settings, "SUPABASE_URL")
    assert hasattr(settings, "SUPABASE_KEY")
    
    # Configuration
    assert settings.API_V1_PREFIX == "/api"
    assert settings.PROJECT_NAME == "Custom HTS Backend"
    assert settings.VERSION == "0.1.0"


def test_settings_cors_origins() -> None:
    """Test CORS origins configuration."""
    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert "http://localhost:5173" in settings.CORS_ORIGINS
