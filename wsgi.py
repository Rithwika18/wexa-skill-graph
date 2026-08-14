"""WSGI application entrypoint for production deployment (e.g., Gunicorn, Render, Railway)."""
from backend.app import create_app

# Expose WSGI callable
application = create_app()

if __name__ == "__main__":
    application.run()
