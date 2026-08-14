# WEXA Skill Graph — System Architecture

## 1. Executive Summary

The **WEXA Skill Graph Application** is an intelligent career guidance and skill pathing platform. It models skills, prerequisite hierarchies, and career roles as an interconnected knowledge graph in **CognoDB**, queried using **openCypher** over the **Bolt protocol** via the official **Neo4j Python Driver**. It features AI/NLP skill extraction from unstructured text, canonical taxonomy normalization, multi-hop graph traversals, career role gap analysis, and dependency-aware topological learning roadmap generation.

---

## 2. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Frontend (Future)                    │
│      (Skill Input, Target Role Selector, Graph Visualizer)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON REST
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask REST API Layer                      │
│   ├── Health Check           (/api/health, /api/health/db)  │
│   ├── Skill Discovery        (/api/skills, /api/skills/<id>)│
│   ├── Multi-Hop Traversal    (/api/skills/<id>/reachable)   │
│   ├── Learning Path Finder   (/api/skill-path)              │
│   ├── Common Prerequisites   (/api/skills/common-prereqs)   │
│   ├── Skill Gap Analysis     (/api/skill-gap)               │
│   ├── AI/NLP Extraction      (/api/skills/extract)          │
│   ├── Skill Normalizer       (/api/skills/normalize)        │
│   └── Career Roles & Paths   (/api/roles, /api/recommendations/role-path)
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼ (In-Memory / Driver)         ▼ (Binary Bolt Wire Protocol)
┌──────────────────────────────┐ ┌────────────────────────────┐
│      Service Layer           │ │      CognoDB Database      │
│  ├── Graph Traversal         │ │                            │
│  ├── NLP Extraction Engine   │ │  ├── openCypher Engine     │
│  ├── Skill Normalizer        │ │  ├── Graph Schema / Nodes  │
│  └── Role Recommendation DAG │ │  └── Property Graph Index  │
└──────────────────────────────┘ └────────────────────────────┘
               │                              ▲
               └────── CognoDB Client ────────┘
                      (Neo4j Python Driver)
```

---

## 3. Technology Stack & Graph Schema

### 3.1. CognoDB & Bolt Protocol
**CognoDB** serves as the persistent graph database storing the career skill taxonomy, domain categories, and prerequisite relationships. It natively supports index-free adjacency graph traversals, shortest-path algorithms, and property graph indexing over the binary **Bolt protocol**.

### 3.2. Graph Schema: Nodes & Relationships
- `(:Skill {name: String})`: Individual skill entities (e.g. `Python`, `Pandas`, `Machine Learning`, `PyTorch`).
- `(:Role {title: String, domain: String, level: String})`: Target career roles (e.g. `Data Analyst`, `Data Scientist`, `Machine Learning Engineer`, `NLP Engineer`).
- `[:PREREQUISITE_OF]`: Directed dependency edges from prerequisite skill to downstream skill (`(:Skill)-[:PREREQUISITE_OF]->(:Skill)`).
- `[:REQUIRES {importance: 'required' | 'preferred'}]`: Directed requirement edges from career role to required or preferred skill (`(:Role)-[:REQUIRES]->(:Skill)`).

---

## 4. Modular AI/NLP Skill Extraction Architecture

```
┌────────────────────────────────────────────────────────┐
│              BaseSkillExtractor (ABC)                  │
└──────────────┬──────────────────────────┬──────────────┘
               │                          │
               ▼                          ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│   RuleBasedSkillExtractor    │ │      LLMSkillExtractor       │
│  - Compiled regex patterns   │ │  - Modular adapter           │
│  - Word-boundary tokenizing  │ │  - Graceful fallback         │
│  - Zero paid dependencies    │ │  - Provider configurable     │
└──────────────────────────────┘ └──────────────────────────────┘
```

- **Extraction**: Ingests raw job descriptions, resumes, or user profile summaries and extracts technical skills.
- **Normalization**: Maps colloquial aliases and surface forms (e.g. `"py3"`, `"pandas lib"`, `"ml"`, `"k8s"`) to canonical taxonomy nodes in the active graph.

---

## 5. Role Recommendation & DAG Learning Roadmap Engine

Given a user's skills and a target career role:
1. **Gap Analysis**: Compares user skills against required and preferred skills for the target role.
2. **Readiness Score**: Calculates percent readiness based on required competencies acquired.
3. **Transitive Prerequisite Resolution**: Discovers missing intermediate prerequisite skills required before learning advanced role competencies.
4. **Kahn's Layered Topological Sorting**: Groups missing skills into sequenced milestone stages (Stage 1 Foundations $\rightarrow$ Stage 2 Intermediate $\rightarrow$ Stage 3 Advanced Frameworks), guaranteeing prerequisites are mastered before downstream skills.

---

## 6. Security & Parameterization Architecture
- **Strict openCypher Parameterization**: All queries use `$param` placeholder dictionaries.
- **Fail-Safe In-Memory Fallback**: Every service layer operates seamlessly with in-memory graph models during testing and offline development.
