import re
from typing import List, Pattern, Set
from backend.services.nlp.base import BaseSkillExtractor


# Comprehensive default skill keyword dictionary and patterns for rule-based extraction
DEFAULT_SKILL_PATTERNS = [
    # Data & AI core skills
    (r"\bpython(?:3)?\b", "Python"),
    (r"\bpandas(?:\s+library)?\b", "Pandas"),
    (r"\bnumpy\b", "NumPy"),
    (r"\bsql(?:\s+database)?\b", "SQL"),
    (r"\bdata\s+analysis\b", "Data Analysis"),
    (r"\bdata\s+analytics\b", "Data Analysis"),
    (r"\bmachine\s+learning\b", "Machine Learning"),
    (r"\bdeep\s+learning\b", "Deep Learning"),
    (r"\bnlp\b", "NLP"),
    (r"\bnatural\s+language\s+processing\b", "NLP"),
    (r"\bpytorch\b", "PyTorch"),
    (r"\btensorflow\b", "TensorFlow"),
    (r"\bscikit-learn\b", "Scikit-Learn"),
    (r"\bsklearn\b", "Scikit-Learn"),
    (r"\bkeras\b", "Keras"),
    (r"\bcomputer\s+vision\b", "Computer Vision"),
    (r"\bcv\b", "Computer Vision"),
    (r"\bgenerative\s+ai\b", "Generative AI"),
    (r"\bgenai\b", "Generative AI"),
    (r"\bllm(?:s)?\b", "LLMs"),
    (r"\blarge\s+language\s+models?\b", "LLMs"),
    # General engineering skills
    (r"\bjavascript\b", "JavaScript"),
    (r"\btypescript\b", "TypeScript"),
    (r"\breact(?:\.js)?\b", "React"),
    (r"\bnode(?:\.js)?\b", "Node.js"),
    (r"\bdocker\b", "Docker"),
    (r"\bkubernetes\b", "Kubernetes"),
    (r"\bk8s\b", "Kubernetes"),
    (r"\baws\b", "AWS"),
    (r"\bgit\b", "Git"),
    (r"\bneo4j\b", "Neo4j"),
    (r"\bcognodb\b", "CognoDB"),
]


class RuleBasedSkillExtractor(BaseSkillExtractor):
    """Deterministic, zero-dependency skill extractor using compiled regex token patterns."""

    def __init__(self) -> None:
        self._compiled_patterns: List[tuple[Pattern, str]] = [
            (re.compile(pattern_str, re.IGNORECASE), canonical_name)
            for pattern_str, canonical_name in DEFAULT_SKILL_PATTERNS
        ]

    def extract_skills(self, text: str) -> List[str]:
        """Extract skill terms from unstructured text using compiled regex patterns.

        Args:
            text: Raw input text.

        Returns:
            List of unique extracted skill names preserving appearance order.
        """
        if not text or not isinstance(text, str):
            return []

        found_skills: List[str] = []
        seen: Set[str] = set()

        for pattern, skill_name in self._compiled_patterns:
            if pattern.search(text):
                if skill_name not in seen:
                    seen.add(skill_name)
                    found_skills.append(skill_name)

        return found_skills
