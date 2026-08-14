from typing import Any, Dict, List, Optional, Set
from backend.graph.cognodb_client import get_cognodb_client
from backend.graph.queries import (
    GET_ALL_ROLES,
    GET_ROLE_DETAILS,
    CHECK_ROLE_EXISTS,
)
from backend.graph.skill_graph import SkillGraph
from backend.services.nlp import get_skill_extractor, get_skill_normalizer


def get_available_roles(graph: Optional[SkillGraph] = None) -> List[Dict[str, Any]]:
    """Retrieve all available career roles from CognoDB or in-memory graph."""
    client = get_cognodb_client()
    if client.is_configured:
        connected, _ = client.check_connectivity()
        if connected:
            records = client.execute_query(GET_ALL_ROLES)
            if records:
                return records

    if graph is not None:
        return graph.get_all_roles()

    return []


def get_role_info(role_title: str, graph: Optional[SkillGraph] = None) -> Dict[str, Any]:
    """Retrieve detailed skill requirements for a specific career role."""
    if not role_title or not isinstance(role_title, str) or not role_title.strip():
        raise ValueError("Role title must be a non-empty string.")

    role_title = role_title.strip()
    client = get_cognodb_client()
    if client.is_configured:
        connected, _ = client.check_connectivity()
        if connected:
            exists_records = client.execute_query(CHECK_ROLE_EXISTS, parameters={"title": role_title})
            if not exists_records or not exists_records[0].get("exists"):
                raise KeyError(f"Career role '{role_title}' not found.")

            records = client.execute_query(GET_ROLE_DETAILS, parameters={"title": role_title})
            if records:
                return records[0]

    if graph is None:
        raise ValueError("SkillGraph instance must be provided when CognoDB is not connected.")

    if not graph.has_role(role_title):
        raise KeyError(f"Career role '{role_title}' not found.")

    return graph.get_role_details(role_title)


def calculate_role_recommendations(
    target_role: str,
    user_skills: Optional[List[str]] = None,
    user_text: Optional[str] = None,
    graph: Optional[SkillGraph] = None
) -> Dict[str, Any]:
    """Calculate career role readiness score and generate an ordered milestone learning roadmap.

    Args:
        target_role: Name/title of target career role.
        user_skills: Optional explicit list of user skill strings.
        user_text: Optional raw text (resume summary, profile, project descriptions).
        graph: Optional in-memory SkillGraph fallback.

    Returns:
        Structured dictionary with gap analysis, readiness percentage, and sequenced learning DAG milestones.
    """
    if not target_role or not isinstance(target_role, str) or not target_role.strip():
        raise ValueError("target_role must be a non-empty string.")

    target_role = target_role.strip()
    normalizer = get_skill_normalizer()

    # 1. Resolve user skills from explicit list and/or unstructured text
    collected_raw_skills: List[str] = []

    if user_skills and isinstance(user_skills, list):
        collected_raw_skills.extend([s for s in user_skills if isinstance(s, str)])

    if user_text and isinstance(user_text, str) and user_text.strip():
        extractor = get_skill_extractor()
        extracted = extractor.extract_skills(user_text)
        collected_raw_skills.extend(extracted)

    normalized_user_skills = normalizer.get_canonical_list(
        collected_raw_skills,
        graph=graph,
        only_in_graph=True
    )
    user_skill_set: Set[str] = set(normalized_user_skills)

    # 2. Fetch role metadata and requirements
    role_info = get_role_info(target_role, graph=graph)
    role_skills_data = role_info.get("required_skills", role_info.get("skills", []))

    required_skills: List[str] = []
    preferred_skills: List[str] = []

    for item in role_skills_data:
        skill_name = item.get("skill")
        importance = item.get("importance", "required")
        if skill_name:
            if importance == "required":
                required_skills.append(skill_name)
            else:
                preferred_skills.append(skill_name)

    all_role_skills = required_skills + preferred_skills

    # 3. Compute acquired vs missing skills
    acquired_skills = [s for s in all_role_skills if s in user_skill_set]
    missing_required = [s for s in required_skills if s not in user_skill_set]
    missing_preferred = [s for s in preferred_skills if s not in user_skill_set]
    all_missing = missing_required + missing_preferred

    # 4. Compute readiness score
    if required_skills:
        acquired_req_count = len([s for s in required_skills if s in user_skill_set])
        readiness_score = round((acquired_req_count / len(required_skills)) * 100, 1)
    else:
        readiness_score = 100.0

    # 5. Build topological learning roadmap
    if graph is None:
        from backend.graph.sample_data import create_sample_skill_graph
        graph = create_sample_skill_graph()

    learning_roadmap = graph.get_topological_learning_order(
        target_skills=all_missing,
        user_known_skills=list(user_skill_set)
    )

    return {
        "target_role": target_role,
        "domain": role_info.get("domain", "General"),
        "level": role_info.get("level", "Mid"),
        "user_skills": normalized_user_skills,
        "role_required_skills": required_skills,
        "role_preferred_skills": preferred_skills,
        "acquired_skills": acquired_skills,
        "missing_required_skills": missing_required,
        "missing_preferred_skills": missing_preferred,
        "all_missing_skills": all_missing,
        "readiness_percentage": readiness_score,
        "learning_roadmap": learning_roadmap,
        "milestones_count": len(learning_roadmap)
    }
