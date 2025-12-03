"""
Flask application entrypoint.
Contains the create_app factory function for initializing the Flask application.
"""

from flask import Flask
from flask_cors import CORS
from routes import register_blueprints


def create_app():
    """
    Application factory function.
    Creates and configures the Flask application instance.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Enable CORS for React Native frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register all route blueprints
    register_blueprints(app)
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)

