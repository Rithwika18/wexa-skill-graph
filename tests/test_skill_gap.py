import pytest
from backend.services.skill_gap import calculate_skill_gap


def test_skill_gap_with_user_skills(sample_graph):
    """Test skill gap calculation when user already has some relevant skills."""
    result = calculate_skill_gap(
        graph=sample_graph,
        user_skills=["Python", "SQL"],
        target_skill="Machine Learning"
    )

    assert result["target_skill"] == "Machine Learning"
    assert result["user_skills"] == ["Python", "SQL"]
    # Path should start from SQL (or Python) to Machine Learning
    assert result["learning_path"][-1] == "Machine Learning"
    assert "Data Analysis" in result["missing_skills"]
    assert "Machine Learning" in result["missing_skills"]
    assert "Python" not in result["missing_skills"]
    assert "SQL" not in result["missing_skills"]


def test_skill_gap_user_already_has_target(sample_graph):
    """Test skill gap when user already possesses the target skill."""
    result = calculate_skill_gap(
        graph=sample_graph,
        user_skills=["Python", "Data Analysis", "Machine Learning"],
        target_skill="Machine Learning"
    )

    assert result["target_skill"] == "Machine Learning"
    assert result["learning_path"] == ["Machine Learning"]
    assert result["missing_skills"] == []


def test_skill_gap_empty_user_skills(sample_graph):
    """Test skill gap when user provides no skills."""
    result = calculate_skill_gap(
        graph=sample_graph,
        user_skills=[],
        target_skill="PyTorch"
    )

    assert result["target_skill"] == "PyTorch"
    assert result["learning_path"][0] == "Python"
    assert result["learning_path"][-1] == "PyTorch"
    assert result["missing_skills"] == result["learning_path"]


def test_skill_gap_nonexistent_target_skill(sample_graph):
    """Test that calculating skill gap for a nonexistent skill raises ValueError."""
    with pytest.raises(ValueError, match="not found in the skill graph"):
        calculate_skill_gap(
            graph=sample_graph,
            user_skills=["Python"],
            target_skill="Quantum Computing"
        )


def test_skill_gap_invalid_target_skill_input(sample_graph):
    """Test invalid target skill input types raise ValueError."""
    with pytest.raises(ValueError):
        calculate_skill_gap(
            graph=sample_graph,
            user_skills=["Python"],
            target_skill=""
        )
    with pytest.raises(ValueError):
        calculate_skill_gap(
            graph=sample_graph,
            user_skills=["Python"],
            target_skill=None
        )
