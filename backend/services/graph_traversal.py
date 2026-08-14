from typing import Any, Dict, List, Optional
from backend.graph.cognodb_client import get_cognodb_client
from backend.graph.queries import (
    CHECK_SKILL_EXISTS,
    GET_REACHABLE_SKILLS,
    GET_SHORTEST_PATH,
    GET_ALL_PATHS,
    GET_COMMON_PREREQUISITES,
    GET_FULL_PREREQUISITE_TREE,
)
from backend.graph.skill_graph import SkillGraph


def _check_skill_exists_cognodb(client, skill_name: str) -> bool:
    """Helper to check if a skill node exists in CognoDB."""
    records = client.execute_query(CHECK_SKILL_EXISTS, parameters={"name": skill_name})
    if records and records[0].get("exists"):
        return True
    return False


def find_reachable_skills(
    start_skill: str,
    max_hops: int = 3,
    min_hops: int = 1,
    graph: Optional[SkillGraph] = None
) -> Dict[str, Any]:
    """Find all skills reachable from a start skill within the specified hop boundaries.

    Args:
        start_skill: Starting skill name.
        max_hops: Maximum traversal depth (relationship hops).
        min_hops: Minimum traversal depth (default 1).
        graph: Optional in-memory SkillGraph fallback.

    Returns:
        Dictionary containing query parameters and list of reachable skills with distances.

    Raises:
        ValueError: If start_skill is empty or hop boundaries are invalid.
        KeyError: If start_skill does not exist in graph.
    """
    if not start_skill or not isinstance(start_skill, str) or not start_skill.strip():
        raise ValueError("start_skill must be a non-empty string.")

    if not isinstance(max_hops, int) or max_hops < 1:
        raise ValueError("max_hops must be a positive integer (>= 1).")

    if not isinstance(min_hops, int) or min_hops < 1:
        raise ValueError("min_hops must be a positive integer (>= 1).")

    if min_hops > max_hops:
        raise ValueError("min_hops cannot be greater than max_hops.")

    start_skill = start_skill.strip()

    # Attempt CognoDB execution if configured and connected
    client = get_cognodb_client()
    if client.is_configured:
        connected, _ = client.check_connectivity()
        if connected:
            if not _check_skill_exists_cognodb(client, start_skill):
                raise KeyError(f"Skill '{start_skill}' not found in the skill graph.")

            params = {
                "start_name": start_skill,
                "max_hops": max_hops,
                "min_hops": min_hops
            }
            records = client.execute_query(GET_REACHABLE_SKILLS, parameters=params)
            return {
                "start_skill": start_skill,
                "min_hops": min_hops,
                "max_hops": max_hops,
                "reachable_skills": records,
                "source": "CognoDB"
            }

    # In-memory graph fallback
    if graph is None:
        raise ValueError("SkillGraph instance must be provided when CognoDB is not connected.")

    if not graph.has_skill(start_skill):
        raise KeyError(f"Skill '{start_skill}' not found in the skill graph.")

    reachable = graph.get_reachable_skills(start_skill, max_hops=max_hops, min_hops=min_hops)
    return {
        "start_skill": start_skill,
        "min_hops": min_hops,
        "max_hops": max_hops,
        "reachable_skills": reachable,
        "source": "in-memory"
    }


def find_learning_paths(
    from_skill: str,
    to_skill: str,
    graph: Optional[SkillGraph] = None
) -> Dict[str, Any]:
    """Find shortest and alternative learning paths between two skills.

    Args:
        from_skill: Prerequisite/starting skill name.
        to_skill: Desired target skill name.
        graph: Optional in-memory SkillGraph fallback.

    Returns:
        Dictionary containing shortest path, path length, and all alternative paths.

    Raises:
        ValueError: If skill names are invalid.
        KeyError: If either skill is not in graph.
    """
    if not from_skill or not isinstance(from_skill, str) or not from_skill.strip():
        raise ValueError("from_skill must be a non-empty string.")
    if not to_skill or not isinstance(to_skill, str) or not to_skill.strip():
        raise ValueError("to_skill must be a non-empty string.")

    from_skill = from_skill.strip()
    to_skill = to_skill.strip()

    client = get_cognodb_client()
    if client.is_configured:
        connected, _ = client.check_connectivity()
        if connected:
            if not _check_skill_exists_cognodb(client, from_skill):
                raise KeyError(f"Skill '{from_skill}' not found in the skill graph.")
            if not _check_skill_exists_cognodb(client, to_skill):
                raise KeyError(f"Skill '{to_skill}' not found in the skill graph.")

            params = {"start_name": from_skill, "target_name": to_skill}
            shortest_records = client.execute_query(GET_SHORTEST_PATH, parameters=params)
            all_records = client.execute_query(GET_ALL_PATHS, parameters=params)

            shortest_path = shortest_records[0]["path"] if shortest_records else None
            path_len = shortest_records[0]["length"] if shortest_records else 0
            all_paths = [r["path"] for r in all_records]

            return {
                "from_skill": from_skill,
                "to_skill": to_skill,
                "path": shortest_path,
                "path_length": path_len,
                "skills_in_path": shortest_path or [],
                "all_paths": all_paths,
                "source": "CognoDB"
            }

    # In-memory graph fallback
    if graph is None:
        raise ValueError("SkillGraph instance must be provided when CognoDB is not connected.")

    if not graph.has_skill(from_skill):
        raise KeyError(f"Skill '{from_skill}' not found in the skill graph.")
    if not graph.has_skill(to_skill):
        raise KeyError(f"Skill '{to_skill}' not found in the skill graph.")

    shortest_path = graph.find_shortest_path(from_skill, to_skill)
    all_paths = graph.find_all_paths(from_skill, to_skill)
    path_len = len(shortest_path) - 1 if shortest_path else 0

    return {
        "from_skill": from_skill,
        "to_skill": to_skill,
        "path": shortest_path,
        "path_length": path_len,
        "skills_in_path": shortest_path or [],
        "all_paths": all_paths,
        "source": "in-memory"
    }


def find_common_prerequisites(
    skill_1: str,
    skill_2: str,
    graph: Optional[SkillGraph] = None
) -> Dict[str, Any]:
    """Find shared foundational prerequisite skills for two distinct target skills.

    Args:
        skill_1: First target skill.
        skill_2: Second target skill.
        graph: Optional in-memory SkillGraph fallback.

    Returns:
        Dictionary with common prerequisite skills, distances, and total distance.
    """
    if not skill_1 or not isinstance(skill_1, str) or not skill_1.strip():
        raise ValueError("skill1 must be a non-empty string.")
    if not skill_2 or not isinstance(skill_2, str) or not skill_2.strip():
        raise ValueError("skill2 must be a non-empty string.")

    skill_1 = skill_1.strip()
    skill_2 = skill_2.strip()

    if skill_1 == skill_2:
        raise ValueError("skill1 and skill2 must be distinct skills.")

    client = get_cognodb_client()
    if client.is_configured:
        connected, _ = client.check_connectivity()
        if connected:
            if not _check_skill_exists_cognodb(client, skill_1):
                raise KeyError(f"Skill '{skill_1}' not found in the skill graph.")
            if not _check_skill_exists_cognodb(client, skill_2):
                raise KeyError(f"Skill '{skill_2}' not found in the skill graph.")

            params = {"skill_1": skill_1, "skill_2": skill_2}
            records = client.execute_query(GET_COMMON_PREREQUISITES, parameters=params)
            return {
                "skill_1": skill_1,
                "skill_2": skill_2,
                "common_prerequisites": records,
                "source": "CognoDB"
            }

    # In-memory graph fallback
    if graph is None:
        raise ValueError("SkillGraph instance must be provided when CognoDB is not connected.")

    if not graph.has_skill(skill_1):
        raise KeyError(f"Skill '{skill_1}' not found in the skill graph.")
    if not graph.has_skill(skill_2):
        raise KeyError(f"Skill '{skill_2}' not found in the skill graph.")

    common = graph.get_common_prerequisites(skill_1, skill_2)
    return {
        "skill_1": skill_1,
        "skill_2": skill_2,
        "common_prerequisites": common,
        "source": "in-memory"
    }


def find_all_prerequisites(
    target_skill: str,
    graph: Optional[SkillGraph] = None
) -> Dict[str, Any]:
    """Find all upstream prerequisite ancestor skills for a target skill.

    Args:
        target_skill: Target skill name.
        graph: Optional in-memory SkillGraph fallback.
    """
    if not target_skill or not isinstance(target_skill, str) or not target_skill.strip():
        raise ValueError("target_skill must be a non-empty string.")

    target_skill = target_skill.strip()

    client = get_cognodb_client()
    if client.is_configured:
        connected, _ = client.check_connectivity()
        if connected:
            if not _check_skill_exists_cognodb(client, target_skill):
                raise KeyError(f"Skill '{target_skill}' not found in the skill graph.")

            params = {"target_name": target_skill}
            records = client.execute_query(GET_FULL_PREREQUISITE_TREE, parameters=params)
            return {
                "target_skill": target_skill,
                "prerequisites": records,
                "source": "CognoDB"
            }

    if graph is None:
        raise ValueError("SkillGraph instance must be provided when CognoDB is not connected.")

    if not graph.has_skill(target_skill):
        raise KeyError(f"Skill '{target_skill}' not found in the skill graph.")

    prereqs = graph.get_all_prerequisites(target_skill)
    return {
        "target_skill": target_skill,
        "prerequisites": prereqs,
        "source": "in-memory"
    }
