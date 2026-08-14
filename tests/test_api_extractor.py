def test_api_extract_skills_success(client):
    """Test POST /api/skills/extract extracts and normalizes skills from text."""
    payload = {
        "text": (
            "We are hiring a Data Scientist proficient in Python, SQL, and Pandas, "
            "with practical experience in Machine Learning and PyTorch."
        )
    }
    response = client.post("/api/skills/extract", json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert "extracted_skills" in data
    assert "normalized_skills" in data
    assert "canonical_skills" in data

    extracted = data["extracted_skills"]
    assert "Python" in extracted
    assert "SQL" in extracted
    assert "Pandas" in extracted
    assert "Machine Learning" in extracted
    assert "PyTorch" in extracted

    # Check normalization details
    norm_map = {item["raw"]: item for item in data["normalized_skills"]}
    assert norm_map["Python"]["canonical"] == "Python"
    assert norm_map["Python"]["in_graph"] is True


def test_api_extract_skills_empty_text(client):
    """Test POST /api/skills/extract with empty text returns 400."""
    response = client.post("/api/skills/extract", json={"text": "   "})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_api_extract_skills_missing_field(client):
    """Test POST /api/skills/extract with missing 'text' key returns 400."""
    response = client.post("/api/skills/extract", json={"content": "Python"})
    assert response.status_code == 400


def test_api_extract_skills_non_json(client):
    """Test POST /api/skills/extract with non-JSON body returns 400."""
    response = client.post("/api/skills/extract", data="raw string text")
    assert response.status_code == 400


def test_api_normalize_skills_success(client):
    """Test POST /api/skills/normalize normalizes raw skill aliases."""
    payload = {
        "skills": ["python3", "sql db", "pandas lib", "k8s"]
    }
    response = client.post("/api/skills/normalize", json=payload)
    assert response.status_code == 200
    data = response.get_json()

    assert "normalized_skills" in data
    assert "canonical_skills" in data
    assert data["count"] == 4

    canonical = data["canonical_skills"]
    assert "Python" in canonical
    assert "SQL" in canonical
    assert "Pandas" in canonical
    assert "Kubernetes" in canonical


def test_api_normalize_skills_invalid_type(client):
    """Test POST /api/skills/normalize with non-list 'skills' returns 400."""
    response = client.post("/api/skills/normalize", json={"skills": "python3"})
    assert response.status_code == 400


def test_api_normalize_skills_missing_field(client):
    """Test POST /api/skills/normalize with missing 'skills' returns 400."""
    response = client.post("/api/skills/normalize", json={})
    assert response.status_code == 400
