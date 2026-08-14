# WEXA Skill Graph — Project Notes & Status

## Current Status: Phase 6 (Career Role Graph & Learning Roadmap Engine) Completed

### Implemented Artifacts
- **Phase 1 (Initial Setup)**: Modular Flask application, environment configuration, `/api/health`, pytest fixtures.
- **Phase 2 (Basic Graph Logic)**: In-memory `SkillGraph`, sample skill relationships, BFS skill-gap algorithm, `/api/skills` and `/api/skill-gap` endpoints.
- **Phase 3 (CognoDB Integration)**: Official Neo4j Python Driver, Bolt protocol connection manager, parameterized openCypher queries, database seed script, database health check endpoints.
- **Phase 4 (Graph Traversal Queries)**:
  - **Parameterized 2+ Hop Reachable Traversal (`GET_REACHABLE_SKILLS`)**: Traverses variable-depth prerequisite trees up to configurable `$max_hops` with `$min_hops` support.
  - **Prerequisite / Learning Path Traversal (`GET_SHORTEST_PATH`, `GET_ALL_PATHS`)**: Finds shortest ordered learning paths and alternative routes between skills.
  - **Graph-Native Common Prerequisites (`GET_COMMON_PREREQUISITES`)**: Discovers shared foundation skills for diverse specializations.
  - **Transitive Upstream Dependencies (`GET_FULL_PREREQUISITE_TREE`)**: Traverses all ancestor prerequisites for a target skill.
  - **REST Endpoints**: `/api/skills/<name>/reachable`, `/api/skill-path`, `/api/skills/common-prerequisites`, `/api/skills/<name>/prerequisites`.
- **Phase 5 (AI/NLP Skill Extraction & Canonical Normalization)**:
  - **Modular Extractor Interface (`BaseSkillExtractor`)**: Provider-agnostic design with zero-dependency rule extractor (`RuleBasedSkillExtractor`), LLM adapter (`LLMSkillExtractor`), and dynamic factory (`get_skill_extractor()`).
  - **Canonical Normalizer (`SkillNormalizer`)**: Resolves surface variations and aliases (`"py3"`, `"pandas lib"`, `"k8s"`) to canonical taxonomy nodes with active graph lookup.
  - **REST Endpoints**: `POST /api/skills/extract`, `POST /api/skills/normalize`.
- **Phase 6 (Career Role Graph & Role-Based Recommendations)**:
  - **Role Schema & Queries (`backend/graph/queries.py`)**: `:Role` nodes with `domain`, `level`, and `:REQUIRES {importance: 'required' | 'preferred'}` directed edges.
  - **Career Roles Seeded into CognoDB**: `Data Analyst`, `Data Scientist`, `Machine Learning Engineer`, `NLP Engineer`.
  - **Topological Learning Roadmap Engine (`backend/services/role_recommendations.py`)**: Calculates career role readiness percentages, acquired vs missing skills, and sequenced milestone DAG roadmaps with prerequisite dependencies.
  - **REST Endpoints**: `GET /api/roles`, `GET /api/roles/<role_name>`, `POST /api/recommendations/role-path`.
- **Automated Test Suite**: **77 tests passing (100% success)** across unit, integration, live CognoDB, and API test suites.

---

## Phased Implementation Roadmap

| Phase | Milestone Description | Target Deliverables | Status |
|---|---|---|---|
| **Phase 1** | **Initial Setup & Scaffolding** | Flask app factory, `/api/health`, config, tests, docs | **Completed** |
| **Phase 2** | **Basic Graph Logic & Local Pathfinding** | In-memory `SkillGraph`, sample data, BFS gap service, REST APIs, tests | **Completed** |
| **Phase 3** | **CognoDB Integration (Bolt & openCypher)** | Neo4j Python Driver, CognoDB client, parameterized queries, seed script | **Completed** |
| **Phase 4** | **Graph Traversal Queries** | 2+ hop traversals, learning pathfinder, common prerequisite graph queries, REST APIs | **Completed** |
| **Phase 5** | **AI/NLP Skill Extraction & Normalization** | Modular skill extraction provider interface, canonical skill mapping, REST APIs | **Completed** |
| **Phase 6** | **Career Role Graph & Learning Roadmap Engine** | Role entities, role requirements graph, topological DAG roadmap generator, REST APIs | **Completed** |

---

## Architectural & Design Principles
1. **Separation of Concerns**: Routes handle HTTP requests and parameter parsing; Services encapsulate business logic; Graph layer provides openCypher queries and in-memory fallbacks; NLP layer handles entity extraction and canonicalization.
2. **Strict Parameterization**: No dynamic string interpolation in Cypher queries; all user inputs are passed safely through `$param` dictionaries.
3. **Seamless Offline / In-Memory Operation**: All services and tests operate reliably both with live CognoDB connections and in offline in-memory graph modes.
