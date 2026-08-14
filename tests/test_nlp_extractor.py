import pytest
from backend.services.nlp import (
    RuleBasedSkillExtractor,
    LLMSkillExtractor,
    SkillNormalizer,
    get_skill_extractor,
    get_skill_normalizer,
)


def test_rule_extractor_basic():
    """Test extracting core programming and data skills from text."""
    extractor = RuleBasedSkillExtractor()
    text = "We are seeking a Backend Engineer with strong Python, SQL, and Pandas experience."
    skills = extractor.extract_skills(text)

    assert "Python" in skills
    assert "SQL" in skills
    assert "Pandas" in skills


def test_rule_extractor_multi_word_and_acronyms():
    """Test extracting multi-word concepts and acronyms."""
    extractor = RuleBasedSkillExtractor()
    text = (
        "Looking for Machine Learning Specialists with Deep Learning, "
        "Natural Language Processing (NLP), and PyTorch or TensorFlow background."
    )
    skills = extractor.extract_skills(text)

    assert "Machine Learning" in skills
    assert "Deep Learning" in skills
    assert "NLP" in skills
    assert "PyTorch" in skills
    assert "TensorFlow" in skills


def test_rule_extractor_empty_and_noise():
    """Test extractor handles empty, non-string, or noise inputs safely."""
    extractor = RuleBasedSkillExtractor()
    assert extractor.extract_skills("") == []
    assert extractor.extract_skills(None) == []
    assert extractor.extract_skills(12345) == []
    assert extractor.extract_skills("This text has no tech buzzwords at all.") == []


def test_skill_normalizer_aliases(sample_graph):
    """Test normalizer resolves colloquial surface variations to canonical names."""
    normalizer = SkillNormalizer()

    item_py = normalizer.normalize_skill("python3", graph=sample_graph)
    assert item_py["canonical"] == "Python"
    assert item_py["in_graph"] is True

    item_pandas = normalizer.normalize_skill("pandas lib", graph=sample_graph)
    assert item_pandas["canonical"] == "Pandas"
    assert item_pandas["in_graph"] is True

    item_ml = normalizer.normalize_skill("ml", graph=sample_graph)
    assert item_ml["canonical"] == "Machine Learning"
    assert item_ml["in_graph"] is True

    item_k8s = normalizer.normalize_skill("k8s", graph=sample_graph)
    assert item_k8s["canonical"] == "Kubernetes"
    assert item_k8s["in_graph"] is False  # Kubernetes is not in the sample skill graph


def test_skill_normalizer_batch_and_deduplication(sample_graph):
    """Test batch normalization and deduplicated canonical list generation."""
    normalizer = SkillNormalizer()
    raw_list = ["py", "python3", "sql db", "pandas", "data analytics", "unknown_tool_xyz"]

    results = normalizer.normalize_skills(raw_list, graph=sample_graph)
    assert len(results) == 6

    canonical_list = normalizer.get_canonical_list(raw_list, graph=sample_graph)
    assert canonical_list == ["Python", "SQL", "Pandas", "Data Analysis", "Unknown_Tool_Xyz"]

    # Filter only skills present in graph
    in_graph_list = normalizer.get_canonical_list(raw_list, graph=sample_graph, only_in_graph=True)
    assert "Unknown_Tool_Xyz" not in in_graph_list
    assert in_graph_list == ["Python", "SQL", "Pandas", "Data Analysis"]


def test_extractor_factory():
    """Test factory instantiates correct extractor types based on provider configuration."""
    rule_ext = get_skill_extractor("rule_based")
    assert isinstance(rule_ext, RuleBasedSkillExtractor)

    regex_ext = get_skill_extractor("regex")
    assert isinstance(regex_ext, RuleBasedSkillExtractor)

    llm_ext = get_skill_extractor("openai")
    assert isinstance(llm_ext, LLMSkillExtractor)


def test_llm_extractor_fallback():
    """Test LLM extractor gracefully falls back to rule extraction when unconfigured."""
    extractor = LLMSkillExtractor(provider="openai", api_key=None)
    assert extractor.is_llm_configured is False

    text = "Proficient in Python and PyTorch."
    skills = extractor.extract_skills(text)
    assert "Python" in skills
    assert "PyTorch" in skills
