from flask import Blueprint, jsonify
from backend.graph.cognodb_client import get_cognodb_client

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint verifying backend and reporting database status safely."""
    client = get_cognodb_client()
    db_configured = client.is_configured
    db_connected = False

    if db_configured:
        db_connected, _ = client.check_connectivity()

    return jsonify({
        "status": "healthy",
        "service": "wexa-skill-graph-api",
        "version": "0.1.0",
        "database": {
            "type": "CognoDB",
            "configured": db_configured,
            "connected": db_connected,
        }
    }), 200


@health_bp.route("/api/health/db", methods=["GET"])
def database_health_check():
    """Detailed database connectivity health endpoint."""
    client = get_cognodb_client()
    configured = client.is_configured

    if not configured:
        return jsonify({
            "database": "CognoDB",
            "status": "unconfigured",
            "message": "CognoDB environment variables are not set."
        }), 200

    connected, message = client.check_connectivity()
    status_code = 200 if connected else 503

    return jsonify({
        "database": "CognoDB",
        "status": "connected" if connected else "disconnected",
        "message": message
    }), status_code
