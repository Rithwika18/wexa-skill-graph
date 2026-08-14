def test_health_check_status_code(client):
    """Test that /api/health returns HTTP status 200."""
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_check_payload(client):
    """Test that /api/health returns the expected JSON response."""
    response = client.get("/api/health")
    data = response.get_json()

    assert data is not None
    assert data.get("status") == "healthy"
    assert data.get("service") == "wexa-skill-graph-api"
    assert "version" in data
