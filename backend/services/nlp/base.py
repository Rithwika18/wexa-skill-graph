from abc import ABC, abstractmethod
from typing import List


class BaseSkillExtractor(ABC):
    """Abstract base interface for modular skill extraction providers."""

    @abstractmethod
    def extract_skills(self, text: str) -> List[str]:
        """Extract skill terms from unstructured text.

        Args:
            text: Raw input text (job description, resume excerpt, etc.).

        Returns:
            List of extracted skill names as strings.
        """
        pass
