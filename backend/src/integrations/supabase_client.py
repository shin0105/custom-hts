"""Supabase client for database operations."""

from typing import Optional, Any
from datetime import datetime, timezone
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

    async def save_financial_statement(
        self, table: str, data: dict[str, Any]
    ) -> bool:
        """
        Save financial statement data to database.

        Args:
            table: Table name (korean_financials or us_financials)
            data: Financial statement data

        Returns:
            True if successful, False otherwise
        """
        if not self._client:
            print("Supabase client not initialized")
            return False

        try:
            response = self._client.table(table).upsert(data).execute()
            return True
        except Exception as e:
            print(f"Failed to save financial statement: {e}")
            return False

    async def get_financial_statement(
        self, table: str, symbol: str, year: int, quarter: Optional[int] = None
    ) -> Optional[dict[str, Any]]:
        """
        Retrieve financial statement from database.

        Args:
            table: Table name
            symbol: Stock symbol
            year: Fiscal year
            quarter: Optional quarter

        Returns:
            Financial statement data or None
        """
        if not self._client:
            return None

        try:
            query = (
                self._client.table(table)
                .select("*")
                .eq("symbol", symbol)
                .eq("year", year)
            )

            if quarter is not None:
                query = query.eq("quarter", quarter)

            response = query.execute()

            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Failed to get financial statement: {e}")
            return None

    def get_kdevelopers_token(
        self, api_key_hash: str
    ) -> Optional[dict[str, Any]]:
        """
        Retrieve cached KDevelopers access token by API key hash.
        """
        if not self._client:
            return None

        try:
            response = (
                self._client.table("kdevelopers_tokens")
                .select("*")
                .eq("api_key_hash", api_key_hash)
                .limit(1)
                .execute()
            )
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Failed to get KDevelopers token: {e}")
            return None

    def save_kdevelopers_token(
        self,
        api_key_hash: str,
        access_token: str,
        expires_at: Optional[datetime],
    ) -> bool:
        """
        Upsert KDevelopers access token by API key hash.
        """
        if not self._client:
            print("Supabase client not initialized")
            return False

        try:
            payload = {
                "api_key_hash": api_key_hash,
                "access_token": access_token,
                "expires_at": expires_at.isoformat() if expires_at else None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            self._client.table("kdevelopers_tokens").upsert(payload).execute()
            return True
        except Exception as e:
            print(f"Failed to save KDevelopers token: {e}")
            return False

    def delete_kdevelopers_token(self, api_key_hash: str) -> bool:
        """
        Delete cached KDevelopers access token by API key hash.
        """
        if not self._client:
            print("Supabase client not initialized")
            return False

        try:
            self._client.table("kdevelopers_tokens").delete().eq(
                "api_key_hash", api_key_hash
            ).execute()
            return True
        except Exception as e:
            print(f"Failed to delete KDevelopers token: {e}")
            return False


# Global instance
supabase_client = SupabaseClient()
