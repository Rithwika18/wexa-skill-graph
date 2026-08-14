def test_api_list_roles(client):
    """Test GET /api/roles returns available career roles."""
    response = client.get("/api/roles")
    assert response.status_code == 200
    data = response.get_json()

    assert "roles" in data
    assert data["count"] >= 4
    titles = [r["title"] for r in data["roles"]]
    assert "Data Analyst" in titles
    assert "Machine Learning Engineer" in titles


def test_api_get_role_details_success(client):
    """Test GET /api/roles/<role_name> returns role requirements."""
    response = client.get("/api/roles/Data%20Scientist")
    assert response.status_code == 200
    data = response.get_json()

    assert data["title"] == "Data Scientist"
    assert "required_skills" in data or "skills" in data


def test_api_get_role_details_not_found(client):
    """Test GET /api/roles/<role_name> with unknown role returns 404."""
    response = client.get("/api/roles/RoboticsSpecialist")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_api_role_recommendation_with_skills_list(client):
    """Test POST /api/recommendations/role-path with user_skills array."""
    payload = {
        "target_role": "Machine Learning Engineer",
        "user_skills": ["Python", "NumPy", "Data Analysis"]
    }
    response = client.post("/api/recommendations/role-path", json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["target_role"] == "Machine Learning Engineer"
    assert "Python" in data["acquired_skills"]
    assert "Deep Learning" in data["missing_required_skills"]
    assert "PyTorch" in data["missing_required_skills"]
    assert "learning_roadmap" in data
    assert len(data["learning_roadmap"]) > 0


def test_api_role_recommendation_with_user_text(client):
    """Test POST /api/recommendations/role-path with unstructured resume text."""
    payload = {
        "target_role": "Data Analyst",
        "user_text": "I have experience working with Python and SQL databases."
    }
    response = client.post("/api/recommendations/role-path", json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["target_role"] == "Data Analyst"
    assert "Python" in data["acquired_skills"]
    assert "SQL" in data["acquired_skills"]
    assert "Pandas" in data["missing_required_skills"]
    assert data["readiness_percentage"] == 50.0


def test_api_role_recommendation_missing_target_role(client):
    """Test POST /api/recommendations/role-path with missing target_role returns 400."""
    response = client.post("/api/recommendations/role-path", json={"user_skills": ["Python"]})
    assert response.status_code == 400


def test_api_role_recommendation_unknown_role(client):
    """Test POST /api/recommendations/role-path with unknown target_role returns 404."""
    response = client.post("/api/recommendations/role-path", json={"target_role": "UnknownRole123"})
    assert response.status_code == 404


def test_api_role_recommendation_non_json(client):
    """Test POST /api/recommendations/role-path with non-JSON payload returns 400."""
    response = client.post("/api/recommendations/role-path", data="text data")
    assert response.status_code == 400
