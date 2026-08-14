import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dotenv import load_dotenv
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import Neo4jError, ServiceUnavailable, AuthError

logger = logging.getLogger(__name__)

# Ensure .env is loaded
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

_UNSET = object()


class CognoDBClient:
    """Client for CognoDB graph database using the official Neo4j Python Driver over Bolt."""

    def __init__(
        self,
        uri: Optional[str] = _UNSET,
        username: Optional[str] = _UNSET,
        password: Optional[str] = _UNSET,
        database: Optional[str] = _UNSET,
    ) -> None:
        self.uri = os.getenv("COGNODB_URI") if uri is _UNSET else uri
        self.username = (
            os.getenv("COGNODB_USERNAME", "cognodb")
            if username is _UNSET
            else username
        )
        self.password = os.getenv("COGNODB_PASSWORD") if password is _UNSET else password
        self.database = os.getenv("COGNODB_DATABASE") if database is _UNSET else database

        self._driver: Optional[Driver] = None

    @property
    def is_configured(self) -> bool:
        """Check whether minimum CognoDB connection parameters are present."""
        return bool(self.uri and self.username and self.password)

    def get_driver(self) -> Driver:
        """Obtain or lazily initialize the Neo4j/Bolt driver instance."""
        if not self.is_configured:
            raise ValueError(
                "CognoDB is not fully configured. Missing COGNODB_URI, COGNODB_USERNAME, or COGNODB_PASSWORD."
            )

        if self._driver is None:
            auth = (self.username, self.password)
            self._driver = GraphDatabase.driver(
                self.uri,
                auth=auth,
                max_connection_lifetime=3600,
                connection_timeout=5.0,
            )
        return self._driver

    def check_connectivity(self) -> Tuple[bool, str]:
        """Perform a safe connectivity check without exposing credentials.

        Returns:
            Tuple of (is_connected: bool, message: str)
        """
        if not self.is_configured:
            return False, "CognoDB configuration incomplete (missing URI, username, or password)."

        try:
            driver = self.get_driver()
            driver.verify_connectivity()
            return True, "Successfully connected to CognoDB via Bolt."
        except AuthError:
            logger.warning("CognoDB authentication failed.")
            return False, "CognoDB authentication failed. Check credentials."
        except ServiceUnavailable as e:
            logger.warning(f"CognoDB service unavailable: {type(e).__name__}")
            return False, "CognoDB service is unavailable at the configured Bolt URI."
        except Exception as e:
            logger.error(f"CognoDB connection error: {type(e).__name__}")
            return False, f"Unable to establish CognoDB connection: {type(e).__name__}"

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute a parameterized openCypher query and return results as Python dictionaries.

        Args:
            query: Parameterized openCypher query string.
            parameters: Dictionary of query parameters.
            database: Optional specific database name.

        Returns:
            List of dictionary records.
        """
        driver = self.get_driver()
        db = database or self.database

        records_list: List[Dict[str, Any]] = []
        with driver.session(database=db) as session:
            result = session.run(query, parameters or {})
            for record in result:
                records_list.append(dict(record))

        return records_list

    def close(self) -> None:
        """Close the underlying driver connection pool cleanly."""
        if self._driver is not None:
            self._driver.close()
            self._driver = None


# Module-level singleton helper
_client_instance: Optional[CognoDBClient] = None


def get_cognodb_client() -> CognoDBClient:
    """Retrieve the global CognoDB client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = CognoDBClient()
    return _client_instance
