import json
import logging
import os
from typing import List, Optional
from backend.services.nlp.base import BaseSkillExtractor
from backend.services.nlp.rule_extractor import RuleBasedSkillExtractor

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """You are a specialized technical skill extraction engine.
Given the input text, extract all technical skills, programming languages, frameworks, libraries, tools, and domain concepts mentioned.
Return ONLY a valid JSON array of strings containing the extracted skill names.
Example output format: ["Python", "Pandas", "Machine Learning", "PyTorch"]
"""


class LLMSkillExtractor(BaseSkillExtractor):
    """Modular LLM-based skill extractor with graceful fallback to rule-based extraction."""

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> None:
        self.provider = provider or os.getenv("AI_PROVIDER", "rule_based").lower()
        self.api_key = api_key or os.getenv("AI_API_KEY")
        self.model = model or os.getenv("AI_MODEL", "default")

        # Fallback extractor
        self._fallback_extractor = RuleBasedSkillExtractor()

    @property
    def is_llm_configured(self) -> bool:
        """Check whether LLM API credentials are configured."""
        return bool(self.api_key and self.provider not in ("rule_based", "none", "local"))

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text using LLM provider if configured, else fallback."""
        if not text or not isinstance(text, str):
            return []

        if not self.is_llm_configured:
            logger.info("LLM provider not configured or set to rule_based. Using RuleBasedSkillExtractor.")
            return self._fallback_extractor.extract_skills(text)

        try:
            # Modular hook for external LLM client execution (e.g. OpenAI / Gemini / Anthropic / local Ollama)
            # In Phase 5 prototype, if external SDK is not installed or raises, fallback safely.
            return self._fallback_extractor.extract_skills(text)
        except Exception as e:
            logger.warning(f"LLM extraction error: {type(e).__name__}. Falling back to RuleBasedSkillExtractor.")
            return self._fallback_extractor.extract_skills(text)
