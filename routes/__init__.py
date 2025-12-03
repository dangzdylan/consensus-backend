"""
Routes package initialization.
Registers all route blueprints with the Flask application.
"""

from routes.auth import auth_bp
from routes.lobby import lobby_bp
from routes.consensus import consensus_bp
from routes.result import result_bp


def register_blueprints(app):
    """
    Register all route blueprints with the Flask application.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(lobby_bp, url_prefix="/api/lobbies")
    app.register_blueprint(consensus_bp, url_prefix="/api/consensus")
    app.register_blueprint(result_bp, url_prefix="/api/results")

