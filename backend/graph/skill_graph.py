from collections import deque
from typing import Any, Dict, List, Optional, Set


class SkillGraph:
    """Directed graph representation of skills, prerequisites, and career role requirements."""

    def __init__(self) -> None:
        # Adjacency list mapping skill name to list of downstream/connected skill names
        self._adjacency: Dict[str, List[str]] = {}
        # Career roles repository: title -> {domain, level, skills: [{skill, importance}]}
        self._roles: Dict[str, Dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # SKILL NODE & RELATIONSHIP OPERATIONS
    # ------------------------------------------------------------------

    def add_skill(self, skill: str) -> None:
        """Add a skill node to the graph if it does not already exist."""
        if not skill or not isinstance(skill, str):
            raise ValueError("Skill name must be a non-empty string.")
        if skill not in self._adjacency:
            self._adjacency[skill] = []

    def add_relationship(self, from_skill: str, to_skill: str) -> None:
        """Add a directed relationship from from_skill to to_skill."""
        self.add_skill(from_skill)
        self.add_skill(to_skill)
        if to_skill not in self._adjacency[from_skill]:
            self._adjacency[from_skill].append(to_skill)

    def has_skill(self, skill: str) -> bool:
        """Check whether a skill exists in the graph."""
        return skill in self._adjacency

    def get_all_skills(self) -> List[str]:
        """Return a list of all skills present in the graph."""
        return list(self._adjacency.keys())

    def get_connected_skills(self, skill: str) -> List[str]:
        """Return the skills directly connected (outgoing edges) from the given skill."""
        if not self.has_skill(skill):
            raise KeyError(f"Skill '{skill}' not found in graph.")
        return list(self._adjacency[skill])

    # ------------------------------------------------------------------
    # CAREER ROLE NODE & REQUIREMENT OPERATIONS
    # ------------------------------------------------------------------

    def add_role(self, title: str, domain: str = "General", level: str = "Mid") -> None:
        """Add a career role node to the graph."""
        if not title or not isinstance(title, str):
            raise ValueError("Role title must be a non-empty string.")
        if title not in self._roles:
            self._roles[title] = {
                "title": title,
                "domain": domain,
                "level": level,
                "skills": []
            }

    def add_role_requirement(
        self,
        role_title: str,
        skill_name: str,
        importance: str = "required"
    ) -> None:
        """Associate a required/preferred skill with a career role."""
        if not self.has_role(role_title):
            self.add_role(role_title)
        self.add_skill(skill_name)

        existing_reqs = self._roles[role_title]["skills"]
        # Update or append
        for req in existing_reqs:
            if req["skill"] == skill_name:
                req["importance"] = importance
                return
        existing_reqs.append({"skill": skill_name, "importance": importance})

    def has_role(self, role_title: str) -> bool:
        """Check whether a career role exists in the graph."""
        return role_title in self._roles

    def get_all_roles(self) -> List[Dict[str, Any]]:
        """Return list of all career roles with basic metadata."""
        return [
            {
                "title": data["title"],
                "domain": data["domain"],
                "level": data["level"]
            }
            for data in self._roles.values()
        ]

    def get_role_details(self, role_title: str) -> Dict[str, Any]:
        """Return detailed information and required skills for a role."""
        if not self.has_role(role_title):
            raise KeyError(f"Career role '{role_title}' not found in graph.")
        return self._roles[role_title]

    # ------------------------------------------------------------------
    # GRAPH TRAVERSAL & PATHFINDING
    # ------------------------------------------------------------------

    def find_shortest_path(self, start_skill: str, end_skill: str) -> Optional[List[str]]:
        """Find the shortest directed path from start_skill to end_skill using BFS."""
        if not self.has_skill(start_skill) or not self.has_skill(end_skill):
            return None

        if start_skill == end_skill:
            return [start_skill]

        queue: deque[List[str]] = deque([[start_skill]])
        visited: Set[str] = {start_skill}

        while queue:
            current_path = queue.popleft()
            current_node = current_path[-1]

            for neighbor in self._adjacency.get(current_node, []):
                if neighbor == end_skill:
                    return current_path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(current_path + [neighbor])

        return None

    def find_all_paths(
        self,
        start_skill: str,
        end_skill: str,
        max_depth: int = 10
    ) -> List[List[str]]:
        """Find all directed paths from start_skill to end_skill up to max_depth using DFS."""
        if not self.has_skill(start_skill) or not self.has_skill(end_skill):
            return []

        if start_skill == end_skill:
            return [[start_skill]]

        all_paths: List[List[str]] = []

        def dfs(current_node: str, current_path: List[str]) -> None:
            if len(current_path) - 1 > max_depth:
                return

            if current_node == end_skill:
                all_paths.append(list(current_path))
                return

            for neighbor in self._adjacency.get(current_node, []):
                if neighbor not in current_path:  # Prevent cycles
                    dfs(neighbor, current_path + [neighbor])

        dfs(start_skill, [start_skill])
        all_paths.sort(key=lambda p: (len(p), p))
        return all_paths

    def get_reachable_skills(
        self,
        start_skill: str,
        max_hops: int = 3,
        min_hops: int = 1
    ) -> List[Dict[str, int]]:
        """Find all downstream skills reachable within [min_hops, max_hops] using BFS."""
        if not self.has_skill(start_skill):
            raise KeyError(f"Skill '{start_skill}' not found in graph.")

        distances: Dict[str, int] = {}
        queue: deque[tuple[str, int]] = deque([(start_skill, 0)])

        while queue:
            node, dist = queue.popleft()
            if dist >= max_hops:
                continue

            for neighbor in self._adjacency.get(node, []):
                if neighbor not in distances or (dist + 1) < distances[neighbor]:
                    distances[neighbor] = dist + 1
                    queue.append((neighbor, dist + 1))

        results = [
            {"skill": skill, "distance": dist}
            for skill, dist in distances.items()
            if dist >= min_hops and dist <= max_hops and skill != start_skill
        ]
        results.sort(key=lambda item: (item["distance"], item["skill"]))
        return results

    def get_all_prerequisites(self, target_skill: str) -> List[Dict[str, int]]:
        """Find all upstream prerequisite skills that lead to target_skill across all depths."""
        if not self.has_skill(target_skill):
            raise KeyError(f"Skill '{target_skill}' not found in graph.")

        prerequisites: List[Dict[str, int]] = []
        for skill in self.get_all_skills():
            if skill != target_skill:
                path = self.find_shortest_path(skill, target_skill)
                if path:
                    prerequisites.append({
                        "skill": skill,
                        "depth": len(path) - 1
                    })

        prerequisites.sort(key=lambda item: (item["depth"], item["skill"]))
        return prerequisites

    def get_common_prerequisites(self, skill_1: str, skill_2: str) -> List[Dict[str, int]]:
        """Find shared prerequisite foundation skills that lead to both skill_1 and skill_2."""
        if not self.has_skill(skill_1):
            raise KeyError(f"Skill '{skill_1}' not found in graph.")
        if not self.has_skill(skill_2):
            raise KeyError(f"Skill '{skill_2}' not found in graph.")
        if skill_1 == skill_2:
            raise ValueError("skill_1 and skill_2 must be distinct skills.")

        common: List[Dict[str, int]] = []
        for candidate in self.get_all_skills():
            if candidate != skill_1 and candidate != skill_2:
                path1 = self.find_shortest_path(candidate, skill_1)
                path2 = self.find_shortest_path(candidate, skill_2)
                if path1 and path2:
                    dist1 = len(path1) - 1
                    dist2 = len(path2) - 1
                    common.append({
                        "skill": candidate,
                        "dist_to_skill1": dist1,
                        "dist_to_skill2": dist2,
                        "total_distance": dist1 + dist2
                    })

        common.sort(key=lambda item: (item["total_distance"], item["skill"]))
        return common

    def get_root_skills(self) -> List[str]:
        """Return skills with in-degree 0 (no prerequisites required)."""
        all_targets: Set[str] = set()
        for targets in self._adjacency.values():
            all_targets.update(targets)
        return [skill for skill in self._adjacency if skill not in all_targets]

    def get_topological_learning_order(
        self,
        target_skills: List[str],
        user_known_skills: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Compute an ordered, multi-stage learning roadmap DAG for a target set of skills.

        Args:
            target_skills: Skills that need to be learned.
            user_known_skills: Skills already mastered by user.

        Returns:
            List of sequenced milestone dictionaries containing step number, title, skills, and prerequisites.
        """
        known_set = set(user_known_skills or [])
        needed_set: Set[str] = set()

        # 1. Expand target skills to include any missing transitive prerequisites
        for target in target_skills:
            if target not in known_set:
                needed_set.add(target)
                if self.has_skill(target):
                    for prereq_item in self.get_all_prerequisites(target):
                        p_skill = prereq_item["skill"]
                        if p_skill not in known_set:
                            needed_set.add(p_skill)

        if not needed_set:
            return []

        # 2. Build local subgraph dependencies among needed_set
        prereqs_of: Dict[str, Set[str]] = {s: set() for s in needed_set}
        for s in needed_set:
            for potential_prereq in needed_set:
                if potential_prereq != s:
                    # If potential_prereq -> s is a direct edge
                    if s in self._adjacency.get(potential_prereq, []):
                        prereqs_of[s].add(potential_prereq)

        # 3. Layered Topological Sorting (Kahn's Algorithm for Stage Partitioning)
        in_degree: Dict[str, int] = {s: len(prereqs_of[s]) for s in needed_set}
        current_layer = [s for s, deg in in_degree.items() if deg == 0]
        completed = set(known_set)

        milestones: List[Dict[str, Any]] = []
        step = 1

        while current_layer:
            current_layer.sort()
            milestone_skills = list(current_layer)

            milestone_details = []
            for s in milestone_skills:
                # Find direct prerequisites (from known or earlier stages)
                direct_prereqs = [
                    p for p in self.get_all_skills()
                    if s in self._adjacency.get(p, []) and p in completed
                ]
                milestone_details.append({
                    "skill": s,
                    "prerequisites": direct_prereqs
                })

            milestones.append({
                "step": step,
                "skills": milestone_skills,
                "skill_details": milestone_details
            })

            # Update degrees
            completed.update(current_layer)
            next_layer = []

            for s in current_layer:
                # Check downstream neighbors in needed_set
                for neighbor in self._adjacency.get(s, []):
                    if neighbor in in_degree:
                        in_degree[neighbor] -= 1
                        if in_degree[neighbor] == 0:
                            next_layer.append(neighbor)

            current_layer = next_layer
            step += 1

        return milestones
