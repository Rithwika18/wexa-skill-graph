from flask import Blueprint, current_app, jsonify, request
from backend.graph.sample_data import create_sample_skill_graph
from backend.services.skill_gap import calculate_skill_gap
from backend.services.graph_traversal import (
    find_reachable_skills,
    find_learning_paths,
    find_common_prerequisites,
    find_all_prerequisites,
)
from backend.services.nlp import get_skill_extractor, get_skill_normalizer
from backend.services.role_recommendations import (
    get_available_roles,
    get_role_info,
    calculate_role_recommendations,
)

skills_bp = Blueprint("skills", __name__, url_prefix="/api")


def get_skill_graph():
    """Helper to retrieve the active SkillGraph from Flask app config or default."""
    graph = current_app.config.get("SKILL_GRAPH")
    if graph is None:
        graph = create_sample_skill_graph()
        current_app.config["SKILL_GRAPH"] = graph
    return graph


@skills_bp.route("/skills", methods=["GET"])
def list_skills():
    """Return all skills available in the graph."""
    graph = get_skill_graph()
    return jsonify({
        "skills": graph.get_all_skills()
    }), 200


@skills_bp.route("/skills/<skill_name>", methods=["GET"])
def get_connected_skills(skill_name: str):
    """Return directly connected outgoing skills (1-hop) for a given skill."""
    graph = get_skill_graph()
    if not graph.has_skill(skill_name):
        return jsonify({
            "error": f"Skill '{skill_name}' not found."
        }), 404

    connected = graph.get_connected_skills(skill_name)
    return jsonify({
        "skill": skill_name,
        "connected_skills": connected
    }), 200


@skills_bp.route("/skills/<skill_name>/reachable", methods=["GET"])
def get_reachable_skills_endpoint(skill_name: str):
    """Find all skills reachable from skill_name within [min_hops, max_hops] (e.g. 2+ hops)."""
    graph = get_skill_graph()

    try:
        max_hops = int(request.args.get("max_hops", 3))
        min_hops = int(request.args.get("min_hops", 1))
    except (ValueError, TypeError):
        return jsonify({
            "error": "Query parameters 'max_hops' and 'min_hops' must be valid integers."
        }), 400

    try:
        result = find_reachable_skills(
            start_skill=skill_name,
            max_hops=max_hops,
            min_hops=min_hops,
            graph=graph
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        return jsonify({"error": str(e).strip("'")}), 404


@skills_bp.route("/skills/<skill_name>/prerequisites", methods=["GET"])
def get_all_prerequisites_endpoint(skill_name: str):
    """Find all upstream prerequisite ancestor skills that lead to skill_name across all depths."""
    graph = get_skill_graph()
    try:
        result = find_all_prerequisites(target_skill=skill_name, graph=graph)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        return jsonify({"error": str(e).strip("'")}), 404


@skills_bp.route("/skill-path", methods=["GET"])
def get_skill_path_endpoint():
    """Find ordered learning path and alternatives from from_skill to to_skill."""
    from_skill = request.args.get("from_skill")
    to_skill = request.args.get("to_skill")

    if not from_skill or not to_skill:
        return jsonify({
            "error": "Both 'from_skill' and 'to_skill' query parameters are required."
        }), 400

    graph = get_skill_graph()
    try:
        result = find_learning_paths(from_skill=from_skill, to_skill=to_skill, graph=graph)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        return jsonify({"error": str(e).strip("'")}), 404


@skills_bp.route("/skills/common-prerequisites", methods=["GET"])
def get_common_prerequisites_endpoint():
    """Find common foundational prerequisite skills shared by two target skills."""
    skill1 = request.args.get("skill1")
    skill2 = request.args.get("skill2")

    if not skill1 or not skill2:
        return jsonify({
            "error": "Both 'skill1' and 'skill2' query parameters are required."
        }), 400

    graph = get_skill_graph()
    try:
        result = find_common_prerequisites(skill_1=skill1, skill_2=skill2, graph=graph)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        return jsonify({"error": str(e).strip("'")}), 404


@skills_bp.route("/skills/extract", methods=["POST"])
def extract_skills_endpoint():
    """Extract and normalize skills from unstructured text (e.g. job description/resume)."""
    if not request.is_json:
        return jsonify({
            "error": "Request body must be valid JSON."
        }), 400

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request payload must be a JSON object."
        }), 400

    text = data.get("text")
    if not text or not isinstance(text, str) or not text.strip():
        return jsonify({
            "error": "Field 'text' is required and must be a non-empty string."
        }), 400

    provider = current_app.config.get("AI_PROVIDER", "rule_based")
    extractor = get_skill_extractor(provider=provider)
    normalizer = get_skill_normalizer()
    graph = get_skill_graph()

    extracted_skills = extractor.extract_skills(text)
    normalized_skills = normalizer.normalize_skills(extracted_skills, graph=graph)
    canonical_skills = normalizer.get_canonical_list(extracted_skills, graph=graph)

    return jsonify({
        "extracted_skills": extracted_skills,
        "normalized_skills": normalized_skills,
        "canonical_skills": canonical_skills,
        "count": len(extracted_skills),
        "extractor": provider
    }), 200


@skills_bp.route("/skills/normalize", methods=["POST"])
def normalize_skills_endpoint():
    """Normalize a list of raw skill strings to canonical graph skills."""
    if not request.is_json:
        return jsonify({
            "error": "Request body must be valid JSON."
        }), 400

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request payload must be a JSON object."
        }), 400

    skills = data.get("skills")
    if skills is None or not isinstance(skills, list):
        return jsonify({
            "error": "Field 'skills' is required and must be a list of strings."
        }), 400

    normalizer = get_skill_normalizer()
    graph = get_skill_graph()

    normalized_skills = normalizer.normalize_skills(skills, graph=graph)
    canonical_skills = normalizer.get_canonical_list(skills, graph=graph)

    return jsonify({
        "normalized_skills": normalized_skills,
        "canonical_skills": canonical_skills,
        "count": len(normalized_skills)
    }), 200


@skills_bp.route("/skill-gap", methods=["POST"])
def compute_skill_gap():
    """Calculate the skill gap and recommended learning path from user skills to target skill."""
    if not request.is_json:
        return jsonify({
            "error": "Request body must be valid JSON."
        }), 400

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request payload must be a JSON object."
        }), 400

    target_skill = data.get("target_skill")
    if not target_skill or not isinstance(target_skill, str) or not target_skill.strip():
        return jsonify({
            "error": "Field 'target_skill' is required and must be a non-empty string."
        }), 400

    user_skills = data.get("user_skills", [])
    if not isinstance(user_skills, list):
        return jsonify({
            "error": "Field 'user_skills' must be a list of skill strings."
        }), 400

    graph = get_skill_graph()
    target_skill = target_skill.strip()

    try:
        result = calculate_skill_gap(graph, user_skills, target_skill)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({
            "error": str(e)
        }), 404


# ----------------------------------------------------------------------
# PHASE 6: CAREER ROLES & ROLE RECOMMENDATION ENDPOINTS
# ----------------------------------------------------------------------

@skills_bp.route("/roles", methods=["GET"])
def list_roles():
    """Return all available career roles."""
    graph = get_skill_graph()
    roles = get_available_roles(graph=graph)
    return jsonify({
        "roles": roles,
        "count": len(roles)
    }), 200


@skills_bp.route("/roles/<role_name>", methods=["GET"])
def get_role_endpoint(role_name: str):
    """Return detailed metadata and required/preferred skills for a career role."""
    graph = get_skill_graph()
    try:
        role_details = get_role_info(role_name, graph=graph)
        return jsonify(role_details), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        return jsonify({"error": str(e).strip("'")}), 404


@skills_bp.route("/recommendations/role-path", methods=["POST"])
def recommend_role_path():
    """Calculate skill gap, readiness percentage, and structured learning roadmap for a target career role."""
    if not request.is_json:
        return jsonify({
            "error": "Request body must be valid JSON."
        }), 400

    data = request.get_json()
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request payload must be a JSON object."
        }), 400

    target_role = data.get("target_role")
    if not target_role or not isinstance(target_role, str) or not target_role.strip():
        return jsonify({
            "error": "Field 'target_role' is required and must be a non-empty string."
        }), 400

    user_skills = data.get("user_skills")
    if user_skills is not None and not isinstance(user_skills, list):
        return jsonify({
            "error": "Field 'user_skills' must be a list of skill strings."
        }), 400

    user_text = data.get("user_text")
    if user_text is not None and not isinstance(user_text, str):
        return jsonify({
            "error": "Field 'user_text' must be a string."
        }), 400

    graph = get_skill_graph()

    try:
        recommendations = calculate_role_recommendations(
            target_role=target_role,
            user_skills=user_skills,
            user_text=user_text,
            graph=graph
        )
        return jsonify(recommendations), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except KeyError as e:
        return jsonify({"error": str(e).strip("'")}), 404
