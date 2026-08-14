def test_get_all_skills_endpoint(client):
    """Test GET /api/skills returns the list of all available skills."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    data = response.get_json()

    assert "skills" in data
    assert isinstance(data["skills"], list)
    assert "Python" in data["skills"]
    assert "Pandas" in data["skills"]
    assert "Machine Learning" in data["skills"]


def test_get_connected_skills_endpoint(client):
    """Test GET /api/skills/<skill_name> returns connected skills."""
    response = client.get("/api/skills/Python")
    assert response.status_code == 200
    data = response.get_json()

    assert data["skill"] == "Python"
    assert set(data["connected_skills"]) == {"Pandas", "NumPy", "SQL"}


def test_get_connected_skills_not_found(client):
    """Test GET /api/skills/<skill_name> with nonexistent skill returns 404."""
    response = client.get("/api/skills/NonExistentSkill")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_post_skill_gap_success(client):
    """Test POST /api/skill-gap returns valid gap and learning path."""
    payload = {
        "user_skills": ["Python", "SQL"],
        "target_skill": "Machine Learning"
    }
    response = client.post("/api/skill-gap", json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert data["target_skill"] == "Machine Learning"
    assert data["user_skills"] == ["Python", "SQL"]
    assert isinstance(data["learning_path"], list)
    assert data["learning_path"][-1] == "Machine Learning"
    assert "Data Analysis" in data["missing_skills"]
    assert "Machine Learning" in data["missing_skills"]


def test_post_skill_gap_missing_target_skill(client):
    """Test POST /api/skill-gap with missing target_skill returns 400."""
    payload = {
        "user_skills": ["Python"]
    }
    response = client.post("/api/skill-gap", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_post_skill_gap_empty_target_skill(client):
    """Test POST /api/skill-gap with empty target_skill returns 400."""
    payload = {
        "user_skills": ["Python"],
        "target_skill": "   "
    }
    response = client.post("/api/skill-gap", json=payload)
    assert response.status_code == 400


def test_post_skill_gap_invalid_user_skills_type(client):
    """Test POST /api/skill-gap with invalid user_skills type returns 400."""
    payload = {
        "user_skills": "Python",
        "target_skill": "Machine Learning"
    }
    response = client.post("/api/skill-gap", json=payload)
    assert response.status_code == 400


def test_post_skill_gap_non_json_request(client):
    """Test POST /api/skill-gap without JSON content type returns 400."""
    response = client.post("/api/skill-gap", data="raw string")
    assert response.status_code == 400


def test_post_skill_gap_nonexistent_target_skill(client):
    """Test POST /api/skill-gap with target skill not in graph returns 404."""
    payload = {
        "user_skills": ["Python"],
        "target_skill": "Cybersecurity"
    }
    response = client.post("/api/skill-gap", json=payload)
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
