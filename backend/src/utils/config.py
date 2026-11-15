"""Configuration management for the HTS backend application."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Korean Investment Securities API
    HANTU_API_KEY: str = os.getenv("HANTU_API_KEY", "")
    HANTU_API_SECRET: str = os.getenv("HANTU_API_SECRET", "")
    HANTU_BASE_URL: str = "https://openapi.koreainvestment.com:9443"

    # OPENDART API
    DART_API_KEY: str = os.getenv("DART_API_KEY", "")
    DART_BASE_URL: str = "https://opendart.fss.or.kr/api"

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")

    # Korean account number
    HANTU_BANK_ACCOUNT: str = os.getenv(
        "HANTU_BANK_ACCOUNT", os.getenv("hantu_bank_account", "")
    )
    HANTU_ACCOUNT_NUMBER: str = (
        os.getenv("HANTU_ACCOUNT_NUMBER", "") or HANTU_BANK_ACCOUNT
    )

    # API Configuration
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "Custom HTS Backend"
    VERSION: str = "0.1.0"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    @classmethod
    def validate(cls) -> list[str]:
        """Warn about missing required variables and return their names.

        Supabase is optional (it only stores financial statements), so its
        variables are not required. Setting just one of SUPABASE_URL and
        SUPABASE_KEY is still reported, because that can never work.
        """
        missing = []
        if not cls.HANTU_API_KEY:
            missing.append("HANTU_API_KEY")
        if not cls.HANTU_API_SECRET:
            missing.append("HANTU_API_SECRET")
        if not cls.DART_API_KEY:
            missing.append("DART_API_KEY")
        if not cls.HANTU_ACCOUNT_NUMBER:
            missing.append("HANTU_ACCOUNT_NUMBER or HANTU_BANK_ACCOUNT")

        if missing:
            print(
                f"Warning: Missing environment variables: {', '.join(missing)}"
            )
            print(
                "Please set these variables in your .env file "
                "for full functionality."
            )

        if bool(cls.SUPABASE_URL) != bool(cls.SUPABASE_KEY):
            print(
                "Warning: Set both SUPABASE_URL and SUPABASE_KEY to store "
                "financial statements, or neither to run without Supabase."
            )

        return missing


settings = Settings()
