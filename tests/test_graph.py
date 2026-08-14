import pytest
from backend.graph.skill_graph import SkillGraph


def test_add_skill(empty_graph):
    """Test adding skills to the graph."""
    empty_graph.add_skill("Python")
    assert empty_graph.has_skill("Python") is True
    assert empty_graph.has_skill("Java") is False
    assert empty_graph.get_all_skills() == ["Python"]


def test_add_invalid_skill(empty_graph):
    """Test that adding an empty or non-string skill raises ValueError."""
    with pytest.raises(ValueError):
        empty_graph.add_skill("")
    with pytest.raises(ValueError):
        empty_graph.add_skill(None)


def test_add_relationship(empty_graph):
    """Test adding directed relationships between skills."""
    empty_graph.add_relationship("Python", "Pandas")
    assert empty_graph.has_skill("Python") is True
    assert empty_graph.has_skill("Pandas") is True
    assert empty_graph.get_connected_skills("Python") == ["Pandas"]
    assert empty_graph.get_connected_skills("Pandas") == []


def test_retrieve_connected_skills(sample_graph):
    """Test retrieving connected downstream skills."""
    python_connected = sample_graph.get_connected_skills("Python")
    assert set(python_connected) == {"Pandas", "NumPy", "SQL"}

    ml_connected = sample_graph.get_connected_skills("Machine Learning")
    assert set(ml_connected) == {"Deep Learning", "NLP"}


def test_get_connected_skills_nonexistent(empty_graph):
    """Test retrieving connected skills for an absent skill raises KeyError."""
    with pytest.raises(KeyError):
        empty_graph.get_connected_skills("Unknown")


def test_find_shortest_path(sample_graph):
    """Test finding the shortest path between connected skills."""
    # Python -> Pandas -> Data Analysis
    path = sample_graph.find_shortest_path("Python", "Data Analysis")
    assert path in [
        ["Python", "Pandas", "Data Analysis"],
        ["Python", "NumPy", "Data Analysis"],
        ["Python", "SQL", "Data Analysis"],
    ]

    # Python -> ... -> PyTorch
    deep_path = sample_graph.find_shortest_path("Python", "PyTorch")
    assert deep_path is not None
    assert deep_path[0] == "Python"
    assert deep_path[-1] == "PyTorch"
    assert "Machine Learning" in deep_path
    assert "Deep Learning" in deep_path


def test_find_path_same_node(sample_graph):
    """Test finding path from a node to itself."""
    path = sample_graph.find_shortest_path("Python", "Python")
    assert path == ["Python"]


def test_find_path_unreachable(empty_graph):
    """Test finding path between disconnected nodes returns None."""
    empty_graph.add_skill("Python")
    empty_graph.add_skill("Rust")
    assert empty_graph.find_shortest_path("Python", "Rust") is None
