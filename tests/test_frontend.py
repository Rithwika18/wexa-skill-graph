def test_frontend_index_route(client):
    """Test that GET / returns the user-facing HTML interface successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"WEXA Skill Graph" in response.data
    assert b"Career Role Roadmap" in response.data
    assert b"AI Skill Extractor" in response.data
    assert b"Graph Traversals" in response.data
