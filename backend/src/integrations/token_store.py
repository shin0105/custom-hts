"""Local file-based cache for KIS (한국투자증권) access tokens.

KIS access tokens are valid for ~24 hours and issuance is rate limited
(1 request per minute per app key), so tokens are cached on disk and
reused across server restarts.

Tokens are stored in a JSON file keyed by the SHA-256 hash of the app key,
so several key pairs can share one cache file. The file is written with
0600 permissions and is gitignored.

Default location: backend/.cache/kis_tokens.json
Override with the HANTU_TOKEN_CACHE_PATH environment variable.
"""

import hashlib
import json
import logging
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_CACHE_PATH = (
    Path(__file__).resolve().parents[2] / ".cache" / "kis_tokens.json"
)


def hash_api_key(api_key: str) -> str:
    """Return the cache key for an app key (never store the key itself)."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


class LocalTokenStore:
    """Thread-safe JSON file store for access tokens."""

    def __init__(self, path: Optional[Path] = None) -> None:
        env_path = os.getenv("HANTU_TOKEN_CACHE_PATH")
        self.path = Path(path or env_path or DEFAULT_CACHE_PATH)
        self._lock = threading.Lock()

    def _read_all(self) -> dict[str, Any]:
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except FileNotFoundError:
            return {}
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("Ignoring unreadable token cache %s: %s", self.path, e)
            return {}

    def _write_all(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        fd = os.open(tmp_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, self.path)
        os.chmod(self.path, 0o600)

    def get(self, api_key_hash: str) -> Optional[dict[str, Any]]:
        """Return {"access_token", "expires_at"} for a key hash, if cached."""
        with self._lock:
            entry = self._read_all().get(api_key_hash)
        return entry if isinstance(entry, dict) else None

    def save(
        self,
        api_key_hash: str,
        access_token: str,
        expires_at: Optional[datetime],
    ) -> bool:
        """Insert or replace the cached token for a key hash."""
        try:
            with self._lock:
                data = self._read_all()
                data[api_key_hash] = {
                    "access_token": access_token,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }
                self._write_all(data)
            return True
        except OSError as e:
            logger.error("Failed to save token cache %s: %s", self.path, e)
            return False

    def delete(self, api_key_hash: str) -> bool:
        """Remove the cached token for a key hash."""
        try:
            with self._lock:
                data = self._read_all()
                if data.pop(api_key_hash, None) is not None:
                    self._write_all(data)
            return True
        except OSError as e:
            logger.error("Failed to update token cache %s: %s", self.path, e)
            return False


token_store = LocalTokenStore()
