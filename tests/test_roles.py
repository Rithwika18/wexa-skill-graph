import pytest
from backend.services.role_recommendations import (
    get_available_roles,
    get_role_info,
    calculate_role_recommendations,
)


def test_skill_graph_roles_basic(sample_graph):
    """Test role nodes and metadata in sample graph."""
    roles = sample_graph.get_all_roles()
    assert len(roles) >= 4

    role_titles = [r["title"] for r in roles]
    assert "Data Analyst" in role_titles
    assert "Data Scientist" in role_titles
    assert "Machine Learning Engineer" in role_titles
    assert "NLP Engineer" in role_titles

    assert sample_graph.has_role("Data Scientist") is True
    assert sample_graph.has_role("NonExistentRole") is False


def test_role_details(sample_graph):
    """Test retrieving requirements for a specific career role."""
    details = sample_graph.get_role_details("Machine Learning Engineer")
    assert details["title"] == "Machine Learning Engineer"
    assert details["domain"] == "AI & Machine Learning"

    skills_map = {item["skill"]: item["importance"] for item in details["skills"]}
    assert "Python" in skills_map
    assert "Machine Learning" in skills_map
    assert "Deep Learning" in skills_map
    assert "PyTorch" in skills_map
    assert skills_map["PyTorch"] == "required"


def test_topological_roadmap_generation(sample_graph):
    """Test DAG-based milestone generation with prerequisite dependency resolution."""
    user_skills = ["Python"]
    target_skills = ["Machine Learning", "PyTorch"]

    milestones = sample_graph.get_topological_learning_order(
        target_skills=target_skills,
        user_known_skills=user_skills
    )

    assert len(milestones) >= 3
    # Step 1 should include intermediate data foundations (e.g. Pandas / NumPy / SQL)
    step1_skills = milestones[0]["skills"]
    # Machine Learning must come after intermediate foundations
    step_ml = next(m["step"] for m in milestones if "Machine Learning" in m["skills"])
    step_pytorch = next(m["step"] for m in milestones if "PyTorch" in m["skills"])
    assert step_ml < step_pytorch


def test_role_recommendations_with_skills_list(sample_graph):
    """Test role recommendation service when given explicit user skill list."""
    result = calculate_role_recommendations(
        target_role="Data Analyst",
        user_skills=["Python", "SQL"],
        graph=sample_graph
    )

    assert result["target_role"] == "Data Analyst"
    assert "Python" in result["acquired_skills"]
    assert "SQL" in result["acquired_skills"]
    assert "Pandas" in result["missing_required_skills"]
    assert "Data Analysis" in result["missing_required_skills"]
    assert result["readiness_percentage"] == 50.0  # 2 of 4 required skills
    assert result["milestones_count"] > 0


def test_role_recommendations_with_text_extraction(sample_graph):
    """Test role recommendation service with unstructured text resume description."""
    user_text = (
        "I am an analyst with experience writing Python code, querying SQL databases, "
        "and performing Data Analysis and building basic Machine Learning models."
    )
    result = calculate_role_recommendations(
        target_role="Machine Learning Engineer",
        user_text=user_text,
        graph=sample_graph
    )

    assert "Python" in result["acquired_skills"]
    assert "Machine Learning" in result["acquired_skills"]
    assert "Deep Learning" in result["missing_required_skills"]
    assert "PyTorch" in result["missing_required_skills"]
    assert len(result["learning_roadmap"]) > 0


def test_role_recommendations_error_handling(sample_graph):
    """Test validation errors for invalid role inputs."""
    with pytest.raises(ValueError):
        calculate_role_recommendations("", graph=sample_graph)

    with pytest.raises(KeyError):
        calculate_role_recommendations("Quantum Astrobiologist", graph=sample_graph)
