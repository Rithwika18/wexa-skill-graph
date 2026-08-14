from typing import Any, Dict, List, Optional
from backend.graph.cognodb_client import get_cognodb_client
from backend.graph.queries import CHECK_SKILL_EXISTS
from backend.graph.skill_graph import SkillGraph

# Standard alias mapping dictionary: surface variation (lowercase) -> canonical skill name
STANDARD_ALIASES: Dict[str, str] = {
    # Python & libraries
    "py": "Python",
    "python": "Python",
    "python3": "Python",
    "py3": "Python",
    "pandas": "Pandas",
    "pandas library": "Pandas",
    "pandas lib": "Pandas",
    "numpy": "NumPy",
    "numpy library": "NumPy",
    "scipy": "SciPy",
    "scikit-learn": "Scikit-Learn",
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    # Data & AI
    "sql": "SQL",
    "sql database": "SQL",
    "sql db": "SQL",
    "data analysis": "Data Analysis",
    "data analytics": "Data Analysis",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "dl": "Deep Learning",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "tf": "TensorFlow",
    "keras": "Keras",
    "computer vision": "Computer Vision",
    "cv": "Computer Vision",
    "generative ai": "Generative AI",
    "genai": "Generative AI",
    "llm": "LLMs",
    "llms": "LLMs",
    "large language models": "LLMs",
    # Cloud & Engineering
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "aws": "AWS",
    "amazon web services": "AWS",
    "react": "React",
    "react.js": "React",
    "reactjs": "React",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "git": "Git",
    "cognodb": "CognoDB",
    "neo4j": "Neo4j",
}


class SkillNormalizer:
    """Normalizes raw extracted skill mentions to canonical skill taxonomy nodes."""

    def __init__(self, custom_aliases: Optional[Dict[str, str]] = None) -> None:
        self._aliases: Dict[str, str] = dict(STANDARD_ALIASES)
        if custom_aliases:
            for k, v in custom_aliases.items():
                self._aliases[k.lower().strip()] = v

    def _is_in_graph(self, skill_name: str, graph: Optional[SkillGraph] = None) -> bool:
        """Check whether a skill exists in CognoDB or fallback in-memory graph."""
        client = get_cognodb_client()
        if client.is_configured:
            connected, _ = client.check_connectivity()
            if connected:
                records = client.execute_query(CHECK_SKILL_EXISTS, parameters={"name": skill_name})
                return bool(records and records[0].get("exists"))

        if graph is not None:
            return graph.has_skill(skill_name)

        return False

    def normalize_skill(
        self,
        raw_skill: str,
        graph: Optional[SkillGraph] = None
    ) -> Dict[str, Any]:
        """Normalize a single raw skill string to its canonical representation.

        Args:
            raw_skill: Input skill term.
            graph: Optional in-memory graph for taxonomy checking.

        Returns:
            Dictionary containing:
                - raw: original string
                - canonical: resolved canonical name
                - in_graph: bool indicating if canonical node exists in database
        """
        if not raw_skill or not isinstance(raw_skill, str):
            return {
                "raw": str(raw_skill),
                "canonical": "",
                "in_graph": False
            }

        cleaned = raw_skill.strip()
        lookup_key = cleaned.lower()

        # 1. Exact alias match
        if lookup_key in self._aliases:
            canonical = self._aliases[lookup_key]
        else:
            # Title-cased fallback
            canonical = cleaned.title()

        in_graph = self._is_in_graph(canonical, graph)

        return {
            "raw": cleaned,
            "canonical": canonical,
            "in_graph": in_graph
        }

    def normalize_skills(
        self,
        raw_skills: List[str],
        graph: Optional[SkillGraph] = None
    ) -> List[Dict[str, Any]]:
        """Normalize a list of raw skill strings."""
        if not raw_skills or not isinstance(raw_skills, list):
            return []

        results: List[Dict[str, Any]] = []
        for raw in raw_skills:
            if isinstance(raw, str) and raw.strip():
                results.append(self.normalize_skill(raw, graph=graph))
        return results

    def get_canonical_list(
        self,
        raw_skills: List[str],
        graph: Optional[SkillGraph] = None,
        only_in_graph: bool = False
    ) -> List[str]:
        """Return a deduplicated list of canonical skill names."""
        normalized = self.normalize_skills(raw_skills, graph=graph)
        canonical_set: List[str] = []
        seen = set()

        for item in normalized:
            canonical = item["canonical"]
            if only_in_graph and not item["in_graph"]:
                continue
            if canonical and canonical not in seen:
                seen.add(canonical)
                canonical_set.append(canonical)

        return canonical_set


# Global singleton normalizer instance
_normalizer_instance: Optional[SkillNormalizer] = None


def get_skill_normalizer() -> SkillNormalizer:
    """Retrieve or create the global SkillNormalizer instance."""
    global _normalizer_instance
    if _normalizer_instance is None:
        _normalizer_instance = SkillNormalizer()
    return _normalizer_instance
