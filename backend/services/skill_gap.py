from typing import Any, Dict, List, Optional
from backend.graph.skill_graph import SkillGraph


def calculate_skill_gap(
    graph: SkillGraph,
    user_skills: List[str],
    target_skill: str
) -> Dict[str, Any]:
    """Calculate the skill gap and recommended learning path to reach target_skill.

    Args:
        graph: The SkillGraph instance.
        user_skills: List of skills the user already possesses.
        target_skill: The desired career/target skill.

    Returns:
        Dictionary containing:
            - target_skill: str
            - user_skills: list of str
            - learning_path: list of str (ordered path from starting skill to target)
            - missing_skills: list of str (skills in path the user needs to learn)

    Raises:
        ValueError: If target_skill is missing, empty, or not found in the graph.
    """
    if not target_skill or not isinstance(target_skill, str):
        raise ValueError("Target skill must be a non-empty string.")

    if not graph.has_skill(target_skill):
        raise ValueError(f"Target skill '{target_skill}' not found in the skill graph.")

    # Normalize user skills list
    sanitized_user_skills = [
        s.strip() for s in user_skills if isinstance(s, str) and s.strip()
    ] if user_skills else []

    # Case 1: User already possesses the target skill
    if target_skill in sanitized_user_skills:
        return {
            "target_skill": target_skill,
            "user_skills": sanitized_user_skills,
            "learning_path": [target_skill],
            "missing_skills": []
        }

    # Case 2: Search for shortest path from any skill the user already possesses
    shortest_path: Optional[List[str]] = None

    for user_skill in sanitized_user_skills:
        if graph.has_skill(user_skill):
            path = graph.find_shortest_path(user_skill, target_skill)
            if path:
                if shortest_path is None or len(path) < len(shortest_path):
                    shortest_path = path

    # Case 3: If no path found from user's current skills, find shortest path from root/entry skills
    if shortest_path is None:
        root_skills = graph.get_root_skills()
        for root in root_skills:
            path = graph.find_shortest_path(root, target_skill)
            if path:
                if shortest_path is None or len(path) < len(shortest_path):
                    shortest_path = path

    # Case 4: Fallback if target skill exists but is disconnected from root skills
    if shortest_path is None:
        # Search all graph nodes for any valid path
        for skill in graph.get_all_skills():
            path = graph.find_shortest_path(skill, target_skill)
            if path:
                if shortest_path is None or len(path) < len(shortest_path):
                    shortest_path = path

    final_path = shortest_path if shortest_path is not None else [target_skill]

    # Compute missing skills along the recommended learning path
    user_skill_set = set(sanitized_user_skills)
    missing_skills = [s for s in final_path if s not in user_skill_set]

    return {
        "target_skill": target_skill,
        "user_skills": sanitized_user_skills,
        "learning_path": final_path,
        "missing_skills": missing_skills
    }
