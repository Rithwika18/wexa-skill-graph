import pytest
from backend.app import create_app
from backend.config import TestingConfig
from backend.graph.sample_data import create_sample_skill_graph
from backend.graph.skill_graph import SkillGraph


@pytest.fixture
def sample_graph() -> SkillGraph:
    """Fixture providing a fresh sample SkillGraph."""
    return create_sample_skill_graph()


@pytest.fixture
def empty_graph() -> SkillGraph:
    """Fixture providing an empty SkillGraph."""
    return SkillGraph()


@pytest.fixture
def app():
    """Create and configure a Flask application instance for testing."""
    app = create_app(config_class=TestingConfig)
    yield app


@pytest.fixture
def client(app):
    """Test client for issuing requests against the application."""
    return app.test_client()
