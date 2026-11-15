"""Supabase client for database operations."""

from typing import Optional
from supabase import create_client, Client
from ..utils.config import settings


class SupabaseClient:
    """Wrapper for Supabase database operations."""

    _instance: Optional["SupabaseClient"] = None
    _client: Optional[Client] = None

    def __new__(cls) -> "SupabaseClient":
        """Singleton pattern to ensure single database connection."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize Supabase client."""
        if self._client is None and settings.SUPABASE_URL:
            try:
                self._client = create_client(
                    settings.SUPABASE_URL, settings.SUPABASE_KEY
                )
            except Exception as e:
                print(f"Failed to initialize Supabase client: {e}")
                self._client = None

    @property
    def client(self) -> Optional[Client]:
        """Get the Supabase client instance."""
        return self._client


# Global instance
supabase_client = SupabaseClient()
