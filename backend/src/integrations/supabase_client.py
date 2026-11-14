"""Supabase client for database operations."""

from typing import Optional, Any
from datetime import datetime
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

    def save_financial_statement(
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
            payload = self._serialize_for_json(data)
            self._client.table(table).upsert(payload).execute()
            return True
        except Exception as e:
            message = str(e)
            if "PGRST205" in message or "Could not find the table" in message:
                print(
                    f"Skipping cache save: table '{table}' not found in Supabase."
                )
                return False
            print(f"Failed to save financial statement: {e}")
            return False

    def get_financial_statement(
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
            message = str(e)
            if "PGRST205" in message or "Could not find the table" in message:
                print(
                    f"Skipping cache read: table '{table}' not found in Supabase."
                )
                return None
            print(f"Failed to get financial statement: {e}")
            return None

    def _serialize_for_json(self, value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: self._serialize_for_json(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._serialize_for_json(v) for v in value]
        return value


# Global instance
supabase_client = SupabaseClient()
