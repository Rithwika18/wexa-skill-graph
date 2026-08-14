import pytest
from backend.services.graph_traversal import (
    find_reachable_skills,
    find_learning_paths,
    find_common_prerequisites,
    find_all_prerequisites,
)
import backend.graph.queries as queries


def test_reachable_skills_2_plus_hops(sample_graph):
    """Test 2+ hop traversal: Python reaches Data Analysis at hop 2 and Machine Learning at hop 3."""
    # min_hops=2, max_hops=3
    result = find_reachable_skills(
        start_skill="Python",
        max_hops=3,
        min_hops=2,
        graph=sample_graph
    )

    reachable_skills = {item["skill"]: item["distance"] for item in result["reachable_skills"]}

    # Hop 1 skills (Pandas, NumPy, SQL) should NOT be present when min_hops=2
    assert "Pandas" not in reachable_skills
    assert "NumPy" not in reachable_skills
    assert "SQL" not in reachable_skills

    # Hop 2 and Hop 3 skills must be present
    assert reachable_skills.get("Data Analysis") == 2
    assert reachable_skills.get("Machine Learning") == 3


def test_reachable_skills_depth_limits(sample_graph):
    """Test max_hops restricts the depth of returned skills."""
    # 1 hop only
    result_1_hop = find_reachable_skills(
        start_skill="Python",
        max_hops=1,
        min_hops=1,
        graph=sample_graph
    )
    skills_1_hop = [item["skill"] for item in result_1_hop["reachable_skills"]]
    assert set(skills_1_hop) == {"Pandas", "NumPy", "SQL"}

    # Full depth 5 hops (should reach PyTorch at depth 5)
    result_5_hops = find_reachable_skills(
        start_skill="Python",
        max_hops=5,
        min_hops=1,
        graph=sample_graph
    )
    skills_5_hops = {item["skill"]: item["distance"] for item in result_5_hops["reachable_skills"]}
    assert "PyTorch" in skills_5_hops
    assert skills_5_hops["PyTorch"] == 5


def test_find_learning_paths_all_paths(sample_graph):
    """Test finding all 3 alternative paths from Python to Machine Learning."""
    result = find_learning_paths(
        from_skill="Python",
        to_skill="Machine Learning",
        graph=sample_graph
    )

    assert result["path_length"] == 3
    assert result["path"] in [
        ["Python", "Pandas", "Data Analysis", "Machine Learning"],
        ["Python", "NumPy", "Data Analysis", "Machine Learning"],
        ["Python", "SQL", "Data Analysis", "Machine Learning"]
    ]
    assert len(result["all_paths"]) == 3
    expected_intermediates = {"Pandas", "NumPy", "SQL"}
    found_intermediates = {p[1] for p in result["all_paths"]}
    assert found_intermediates == expected_intermediates


def test_common_prerequisites(sample_graph):
    """Test graph-native query finding common foundational prerequisites between NLP and PyTorch."""
    result = find_common_prerequisites(
        skill_1="NLP",
        skill_2="PyTorch",
        graph=sample_graph
    )

    common_skills = {item["skill"]: item for item in result["common_prerequisites"]}

    # Machine Learning is 1 hop from NLP and 2 hops from PyTorch
    assert "Machine Learning" in common_skills
    assert common_skills["Machine Learning"]["dist_to_skill1"] == 1
    assert common_skills["Machine Learning"]["dist_to_skill2"] == 2
    assert common_skills["Machine Learning"]["total_distance"] == 3

    # Data Analysis and Python are also shared ancestors
    assert "Data Analysis" in common_skills
    assert "Python" in common_skills


def test_all_prerequisites_tree(sample_graph):
    """Test finding all upstream prerequisite ancestors for Machine Learning."""
    result = find_all_prerequisites(
        target_skill="Machine Learning",
        graph=sample_graph
    )

    prereq_names = [item["skill"] for item in result["prerequisites"]]
    assert "Data Analysis" in prereq_names
    assert "Pandas" in prereq_names
    assert "NumPy" in prereq_names
    assert "SQL" in prereq_names
    assert "Python" in prereq_names
    assert "PyTorch" not in prereq_names


def test_traversal_error_handling(sample_graph):
    """Test validation errors for traversal inputs."""
    with pytest.raises(ValueError):
        find_reachable_skills("", graph=sample_graph)
    with pytest.raises(ValueError):
        find_reachable_skills("Python", max_hops=-1, graph=sample_graph)
    with pytest.raises(ValueError):
        find_reachable_skills("Python", min_hops=4, max_hops=2, graph=sample_graph)
    with pytest.raises(KeyError):
        find_reachable_skills("NonExistent", graph=sample_graph)

    with pytest.raises(ValueError):
        find_common_prerequisites("Python", "Python", graph=sample_graph)


def test_queries_parameter_placeholders():
    """Verify openCypher queries in queries.py have required parameter placeholders."""
    assert "$start_name" in queries.GET_REACHABLE_SKILLS
    assert "$max_hops" in queries.GET_REACHABLE_SKILLS
    assert "$min_hops" in queries.GET_REACHABLE_SKILLS

    assert "$start_name" in queries.GET_ALL_PATHS
    assert "$target_name" in queries.GET_ALL_PATHS

    assert "$skill_1" in queries.GET_COMMON_PREREQUISITES
    assert "$skill_2" in queries.GET_COMMON_PREREQUISITES

    assert "$target_name" in queries.GET_FULL_PREREQUISITE_TREE
