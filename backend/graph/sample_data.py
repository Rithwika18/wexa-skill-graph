from typing import Dict, List, Tuple
from backend.graph.skill_graph import SkillGraph


SAMPLE_RELATIONSHIPS: List[Tuple[str, str]] = [
    ("Python", "Pandas"),
    ("Python", "NumPy"),
    ("Python", "SQL"),
    ("Pandas", "Data Analysis"),
    ("NumPy", "Data Analysis"),
    ("SQL", "Data Analysis"),
    ("Data Analysis", "Machine Learning"),
    ("Machine Learning", "Deep Learning"),
    ("Machine Learning", "NLP"),
    ("Deep Learning", "PyTorch"),
]

# Career role definitions: title -> {domain, level, required_skills, preferred_skills}
SAMPLE_ROLES: Dict[str, Dict[str, any]] = {
    "Data Analyst": {
        "domain": "Data Analytics",
        "level": "Entry / Mid",
        "skills": [
            ("Python", "required"),
            ("SQL", "required"),
            ("Pandas", "required"),
            ("Data Analysis", "required"),
            ("NumPy", "preferred"),
        ]
    },
    "Data Scientist": {
        "domain": "AI & Data Science",
        "level": "Mid",
        "skills": [
            ("Python", "required"),
            ("SQL", "required"),
            ("Pandas", "required"),
            ("NumPy", "required"),
            ("Data Analysis", "required"),
            ("Machine Learning", "required"),
            ("Deep Learning", "preferred"),
        ]
    },
    "Machine Learning Engineer": {
        "domain": "AI & Machine Learning",
        "level": "Mid / Senior",
        "skills": [
            ("Python", "required"),
            ("NumPy", "required"),
            ("Data Analysis", "required"),
            ("Machine Learning", "required"),
            ("Deep Learning", "required"),
            ("PyTorch", "required"),
        ]
    },
    "NLP Engineer": {
        "domain": "Natural Language Processing",
        "level": "Senior",
        "skills": [
            ("Python", "required"),
            ("Data Analysis", "required"),
            ("Machine Learning", "required"),
            ("NLP", "required"),
            ("Deep Learning", "required"),
            ("PyTorch", "preferred"),
        ]
    }
}


def create_sample_skill_graph() -> SkillGraph:
    """Create and return a SkillGraph populated with standard sample skills and career roles."""
    graph = SkillGraph()

    # Add prerequisite skill relationships
    for from_skill, to_skill in SAMPLE_RELATIONSHIPS:
        graph.add_relationship(from_skill, to_skill)

    # Add career roles and requirements
    for role_title, role_data in SAMPLE_ROLES.items():
        graph.add_role(
            title=role_title,
            domain=role_data["domain"],
            level=role_data["level"]
        )
        for skill_name, importance in role_data["skills"]:
            graph.add_role_requirement(role_title, skill_name, importance=importance)

    return graph
