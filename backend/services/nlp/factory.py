import os
from typing import Optional
from backend.services.nlp.base import BaseSkillExtractor
from backend.services.nlp.rule_extractor import RuleBasedSkillExtractor
from backend.services.nlp.llm_extractor import LLMSkillExtractor


def get_skill_extractor(provider: Optional[str] = None) -> BaseSkillExtractor:
    """Factory function to resolve and instantiate the configured skill extractor.

    Args:
        provider: Optional explicit provider name ('rule_based', 'openai', 'gemini', etc.).
                  If None, reads from AI_PROVIDER environment variable.

    Returns:
        Instance of BaseSkillExtractor.
    """
    active_provider = (provider or os.getenv("AI_PROVIDER", "rule_based")).lower().strip()

    if active_provider in ("rule_based", "regex", "default", "local", "none"):
        return RuleBasedSkillExtractor()

    # Any LLM or external model provider
    return LLMSkillExtractor(provider=active_provider)
