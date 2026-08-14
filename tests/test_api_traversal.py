def test_api_get_reachable_skills_2_plus_hops(client):
    """Test GET /api/skills/<name>/reachable with min_hops=2 and max_hops=3."""
    response = client.get("/api/skills/Python/reachable?min_hops=2&max_hops=3")
    assert response.status_code == 200
    data = response.get_json()

    assert data["start_skill"] == "Python"
    assert data["min_hops"] == 2
    assert data["max_hops"] == 3
    reachable_map = {item["skill"]: item["distance"] for item in data["reachable_skills"]}

    assert "Pandas" not in reachable_map
    assert reachable_map.get("Data Analysis") == 2
    assert reachable_map.get("Machine Learning") == 3


def test_api_get_reachable_skills_invalid_params(client):
    """Test GET /api/skills/<name>/reachable with non-integer query params."""
    response = client.get("/api/skills/Python/reachable?max_hops=invalid")
    assert response.status_code == 400


def test_api_get_reachable_skills_not_found(client):
    """Test GET /api/skills/<name>/reachable for nonexistent skill returns 404."""
    response = client.get("/api/skills/Quantum/reachable")
    assert response.status_code == 404


def test_api_get_skill_path_success(client):
    """Test GET /api/skill-path from Python to Machine Learning."""
    response = client.get("/api/skill-path?from_skill=Python&to_skill=Machine%20Learning")
    assert response.status_code == 200
    data = response.get_json()

    assert data["from_skill"] == "Python"
    assert data["to_skill"] == "Machine Learning"
    assert data["path_length"] == 3
    assert len(data["all_paths"]) == 3
    assert data["path"] in data["all_paths"]


def test_api_get_skill_path_missing_params(client):
    """Test GET /api/skill-path without parameters returns 400."""
    response = client.get("/api/skill-path?from_skill=Python")
    assert response.status_code == 400


def test_api_get_skill_path_not_found(client):
    """Test GET /api/skill-path with unknown skill returns 404."""
    response = client.get("/api/skill-path?from_skill=Python&to_skill=Unknown")
    assert response.status_code == 404


def test_api_get_common_prerequisites_success(client):
    """Test GET /api/skills/common-prerequisites for NLP and PyTorch."""
    response = client.get("/api/skills/common-prerequisites?skill1=NLP&skill2=PyTorch")
    assert response.status_code == 200
    data = response.get_json()

    assert data["skill_1"] == "NLP"
    assert data["skill_2"] == "PyTorch"
    skills = [item["skill"] for item in data["common_prerequisites"]]
    assert "Machine Learning" in skills
    assert "Data Analysis" in skills
    assert "Python" in skills


def test_api_get_common_prerequisites_same_skill_error(client):
    """Test GET /api/skills/common-prerequisites with identical skills returns 400."""
    response = client.get("/api/skills/common-prerequisites?skill1=Python&skill2=Python")
    assert response.status_code == 400


def test_api_get_common_prerequisites_missing_params(client):
    """Test GET /api/skills/common-prerequisites without parameters returns 400."""
    response = client.get("/api/skills/common-prerequisites")
    assert response.status_code == 400


def test_api_get_prerequisites_endpoint(client):
    """Test GET /api/skills/<name>/prerequisites returns all ancestor prerequisites."""
    response = client.get("/api/skills/Machine%20Learning/prerequisites")
    assert response.status_code == 200
    data = response.get_json()

    assert data["target_skill"] == "Machine Learning"
    prereqs = [item["skill"] for item in data["prerequisites"]]
    assert "Data Analysis" in prereqs
    assert "Python" in prereqs
