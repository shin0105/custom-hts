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


class _FullyConfigured(Settings):
    HANTU_API_KEY = "your_api_key"
    HANTU_API_SECRET = "your_api_secret"
    DART_API_KEY = "your_dart_key"
    HANTU_ACCOUNT_NUMBER = "12345678"
    SUPABASE_URL = ""
    SUPABASE_KEY = ""


def test_validate_does_not_require_supabase(capsys) -> None:
    """Supabase is optional, so leaving it out is not a warning."""
    assert _FullyConfigured.validate() == []
    assert capsys.readouterr().out == ""


def test_validate_reports_missing_required_keys(capsys) -> None:
    class MissingDart(_FullyConfigured):
        DART_API_KEY = ""

    assert MissingDart.validate() == ["DART_API_KEY"]
    out = capsys.readouterr().out
    assert "DART_API_KEY" in out
    assert "SUPABASE" not in out


def test_validate_warns_on_half_configured_supabase(capsys) -> None:
    class HalfSupabase(_FullyConfigured):
        SUPABASE_URL = "https://your-project.supabase.co"

    assert HalfSupabase.validate() == []
    assert "SUPABASE_KEY" in capsys.readouterr().out
