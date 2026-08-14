import os
from unittest.mock import MagicMock, patch
import pytest
from neo4j.exceptions import AuthError, ServiceUnavailable

from backend.graph.cognodb_client import CognoDBClient
import backend.graph.queries as queries


def test_cognodb_client_unconfigured():
    """Test client handles absent configuration gracefully."""
    client = CognoDBClient(uri=None, username=None, password=None)
    assert client.is_configured is False

    connected, message = client.check_connectivity()
    assert connected is False
    assert "incomplete" in message.lower()

    with pytest.raises(ValueError, match="not fully configured"):
        client.get_driver()


def test_cognodb_client_handles_auth_error():
    """Test client catches AuthError without leaking credentials."""
    client = CognoDBClient(
        uri="bolt://localhost:7687",
        username="cognodb",
        password="test_secret_password"
    )
    assert client.is_configured is True

    with patch("backend.graph.cognodb_client.GraphDatabase.driver") as mock_driver_factory:
        mock_driver = MagicMock()
        mock_driver.verify_connectivity.side_effect = AuthError("Invalid auth")
        mock_driver_factory.return_value = mock_driver

        connected, message = client.check_connectivity()
        assert connected is False
        assert "authentication failed" in message.lower()
        # Verify password is not in the message
        assert "test_secret_password" not in message


def test_cognodb_client_handles_service_unavailable():
    """Test client catches ServiceUnavailable without crashing."""
    client = CognoDBClient(
        uri="bolt://localhost:7687",
        username="cognodb",
        password="secret_password"
    )

    with patch("backend.graph.cognodb_client.GraphDatabase.driver") as mock_driver_factory:
        mock_driver = MagicMock()
        mock_driver.verify_connectivity.side_effect = ServiceUnavailable("Cannot connect")
        mock_driver_factory.return_value = mock_driver

        connected, message = client.check_connectivity()
        assert connected is False
        assert "unavailable" in message.lower()
        assert "secret_password" not in message


def test_cognodb_client_query_execution_mocked():
    """Test execute_query returns dictionary records properly."""
    client = CognoDBClient(
        uri="bolt://localhost:7687",
        username="cognodb",
        password="test_password"
    )

    mock_driver = MagicMock()
    mock_session = MagicMock()
    mock_driver.session.return_value.__enter__.return_value = mock_session

    # Mock session.run returning records
    record_1 = {"name": "Python"}
    record_2 = {"name": "Pandas"}
    mock_session.run.return_value = [record_1, record_2]

    with patch.object(client, "get_driver", return_value=mock_driver):
        results = client.execute_query(queries.GET_ALL_SKILLS)
        assert results == [{"name": "Python"}, {"name": "Pandas"}]
        mock_session.run.assert_called_once_with(queries.GET_ALL_SKILLS, {})


def test_cognodb_queries_parameterization():
    """Verify that all predefined queries use openCypher parameters and no raw concatenations."""
    assert "$name" in queries.UPSERT_SKILL
    assert "$from_name" in queries.UPSERT_PREREQUISITE_RELATIONSHIP
    assert "$to_name" in queries.UPSERT_PREREQUISITE_RELATIONSHIP
    assert "$name" in queries.GET_CONNECTED_SKILLS
    assert "$name" in queries.CHECK_SKILL_EXISTS
    assert "$start_name" in queries.GET_SHORTEST_PATH
    assert "$target_name" in queries.GET_SHORTEST_PATH

    # Verify key openCypher clauses
    assert "MERGE" in queries.UPSERT_SKILL
    assert "PREREQUISITE_OF" in queries.UPSERT_PREREQUISITE_RELATIONSHIP
    assert "MATCH" in queries.GET_ALL_SKILLS


def test_health_endpoint_database_status(client):
    """Test GET /api/health returns database field in payload."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()

    assert "database" in data
    assert data["database"]["type"] == "CognoDB"
    assert "configured" in data["database"]
    assert "connected" in data["database"]


def test_database_health_endpoint_unconfigured(client):
    """Test GET /api/health/db returns unconfigured status when no env vars are present."""
    response = client.get("/api/health/db")
    assert response.status_code == 200
    data = response.get_json()

    assert data["database"] == "CognoDB"
    assert "status" in data


@pytest.mark.skipif(
    not os.getenv("COGNODB_URI") or not os.getenv("COGNODB_PASSWORD"),
    reason="CognoDB live credentials not present in environment"
)
def test_live_cognodb_connectivity():
    """Live integration test against real CognoDB instance when configured."""
    client = CognoDBClient()
    connected, message = client.check_connectivity()
    assert connected is True, f"Live CognoDB connection failed: {message}"
