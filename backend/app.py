from pathlib import Path
from flask import Flask, render_template
from backend.config import get_config, Config
from backend.routes.health import health_bp
from backend.routes.skills import skills_bp
from backend.graph.sample_data import create_sample_skill_graph

BASE_DIR = Path(__file__).resolve().parent


def create_app(config_class=None) -> Flask:
    """Application factory for WEXA Skill Graph Flask backend.

    Args:
        config_class: Configuration class to use. If None, loaded via get_config().

    Returns:
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    # Load configuration
    active_config = config_class or get_config()
    app.config.from_object(active_config)

    # Initialize in-memory skill graph if not already configured
    if "SKILL_GRAPH" not in app.config:
        app.config["SKILL_GRAPH"] = create_sample_skill_graph()

    # Register route blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(skills_bp)

    # User-facing web application frontend root
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    host = app.config.get("HOST", "127.0.0.1")
    port = app.config.get("PORT", 5000)
    debug = app.config.get("DEBUG", True)
    print(f"Starting WEXA Skill Graph Web App on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
