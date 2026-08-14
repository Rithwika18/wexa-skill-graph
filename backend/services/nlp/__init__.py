"""AI/NLP skill extraction and canonical normalization package."""
from backend.services.nlp.base import BaseSkillExtractor
from backend.services.nlp.rule_extractor import RuleBasedSkillExtractor
from backend.services.nlp.llm_extractor import LLMSkillExtractor
from backend.services.nlp.normalizer import SkillNormalizer, get_skill_normalizer
from backend.services.nlp.factory import get_skill_extractor

__all__ = [
    "BaseSkillExtractor",
    "RuleBasedSkillExtractor",
    "LLMSkillExtractor",
    "SkillNormalizer",
    "get_skill_normalizer",
    "get_skill_extractor",
]
