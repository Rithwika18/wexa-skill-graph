"""Centralized openCypher queries for CognoDB.

All queries are strictly parameterized to prevent Cypher injection, ensure safety,
and optimize query execution plan caching.
"""

# Upsert a single Skill node by name
UPSERT_SKILL = """
MERGE (s:Skill {name: $name})
RETURN s.name AS name
"""

# Upsert a directed PREREQUISITE_OF relationship between two skills
UPSERT_PREREQUISITE_RELATIONSHIP = """
MERGE (from_skill:Skill {name: $from_name})
MERGE (to_skill:Skill {name: $to_name})
MERGE (from_skill)-[r:PREREQUISITE_OF]->(to_skill)
RETURN from_skill.name AS from_skill, to_skill.name AS to_skill
"""

# Retrieve all skills ordered alphabetically
GET_ALL_SKILLS = """
MATCH (s:Skill)
RETURN s.name AS name
ORDER BY s.name ASC
"""

# Retrieve all directly connected downstream skills (1-hop outgoing)
GET_CONNECTED_SKILLS = """
MATCH (s:Skill {name: $name})-[:PREREQUISITE_OF]->(target:Skill)
RETURN target.name AS name
ORDER BY target.name ASC
"""

# Check whether a skill exists in the graph
CHECK_SKILL_EXISTS = """
MATCH (s:Skill {name: $name})
RETURN count(s) > 0 AS exists
"""

# ----------------------------------------------------------------------
# PHASE 4: ADVANCED GRAPH TRAVERSAL QUERIES
# ----------------------------------------------------------------------

# Query 1: Parameterized 2+ Hop Reachable Skills Traversal
# Traverses variable-length directed prerequisite paths from $start_name up to $max_hops (defaulting to >= 2 hops).
# Returns each reachable skill along with its minimum hop distance.
GET_REACHABLE_SKILLS = """
MATCH p = (s:Skill {name: $start_name})-[:PREREQUISITE_OF*1..10]->(target:Skill)
WHERE length(p) <= $max_hops AND length(p) >= $min_hops
WITH target, min(length(p)) AS distance
RETURN target.name AS skill, distance
ORDER BY distance ASC, skill ASC
"""

# Query 2A: Shortest Prerequisite / Learning Path
# Finds the shortest directed learning path between two skills.
GET_SHORTEST_PATH = """
MATCH p = (start:Skill {name: $start_name})-[:PREREQUISITE_OF*1..10]->(target:Skill {name: $target_name})
RETURN [node in nodes(p) | node.name] AS path, length(p) AS length
ORDER BY length ASC
LIMIT 1
"""

# Query 2B: All Prerequisite / Learning Paths
# Finds all alternative directed learning paths between two skills (up to 10 hops).
GET_ALL_PATHS = """
MATCH p = (start:Skill {name: $start_name})-[:PREREQUISITE_OF*1..10]->(target:Skill {name: $target_name})
RETURN [node in nodes(p) | node.name] AS path, length(p) AS length
ORDER BY length ASC
"""

# Query 3: Graph-Native Common Prerequisite Foundation
# Finds shared foundational prerequisite skills connecting two distinct target skills across arbitrary variable depths.
# Demonstrates pattern matching that is difficult/inefficient to express in relational SQL (which would require multiple recursive CTEs).
GET_COMMON_PREREQUISITES = """
MATCH p1 = (common:Skill)-[:PREREQUISITE_OF*1..10]->(target1:Skill {name: $skill_1}),
      p2 = (common)-[:PREREQUISITE_OF*1..10]->(target2:Skill {name: $skill_2})
WHERE target1 <> target2
WITH common, min(length(p1)) AS dist_to_skill1, min(length(p2)) AS dist_to_skill2
RETURN common.name AS skill,
       dist_to_skill1,
       dist_to_skill2,
       (dist_to_skill1 + dist_to_skill2) AS total_distance
ORDER BY total_distance ASC, skill ASC
"""

# Query 4: Full Transitive Upstream Prerequisite Tree
# Traverses all upstream prerequisite ancestors for a given target skill across all depths.
GET_FULL_PREREQUISITE_TREE = """
MATCH p = (prereq:Skill)-[:PREREQUISITE_OF*1..10]->(target:Skill {name: $target_name})
WITH prereq, min(length(p)) AS depth
RETURN prereq.name AS skill, depth
ORDER BY depth ASC, skill ASC
"""

# ----------------------------------------------------------------------
# PHASE 6: CAREER ROLES & REQUIREMENTS QUERIES
# ----------------------------------------------------------------------

# Upsert a Career Role node by title
UPSERT_ROLE = """
MERGE (r:Role {title: $title})
SET r.domain = $domain, r.level = $level
RETURN r.title AS title, r.domain AS domain, r.level AS level
"""

# Upsert a directed REQUIRES relationship from Role to Skill
UPSERT_ROLE_REQUIREMENT = """
MERGE (r:Role {title: $title})
MERGE (s:Skill {name: $skill_name})
MERGE (r)-[req:REQUIRES {importance: $importance}]->(s)
RETURN r.title AS role, s.name AS skill, req.importance AS importance
"""

# Retrieve all career roles
GET_ALL_ROLES = """
MATCH (r:Role)
RETURN r.title AS title, r.domain AS domain, r.level AS level
ORDER BY r.title ASC
"""

# Retrieve detailed requirements for a career role
GET_ROLE_DETAILS = """
MATCH (r:Role {title: $title})
OPTIONAL MATCH (r)-[req:REQUIRES]->(s:Skill)
RETURN r.title AS title,
       r.domain AS domain,
       r.level AS level,
       collect({skill: s.name, importance: coalesce(req.importance, 'required')}) AS required_skills
"""

# Check whether a role exists in the graph
CHECK_ROLE_EXISTS = """
MATCH (r:Role {title: $title})
RETURN count(r) > 0 AS exists
"""

# Retrieve roles that require a specific skill
GET_ROLES_FOR_SKILL = """
MATCH (r:Role)-[req:REQUIRES]->(s:Skill {name: $skill_name})
RETURN r.title AS title, r.domain AS domain, req.importance AS importance
ORDER BY r.title ASC
"""
