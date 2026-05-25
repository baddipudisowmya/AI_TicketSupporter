"""
Main Flask Application Factory

This file is the primary entry point for the Flask application.
Its main responsibilities are:
- Creating the Flask app instance.
- Loading environment variables.
- Configuring logging and CORS.
- Registering API blueprints from the 'routes' module.
- Defining a root health-check endpoint.
"""
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

def create_app():
    # Load environment variables from .env file
    load_dotenv()

    app = Flask(__name__)

    # Configure CORS to allow requests from your React frontend
    CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_URL", "http://localhost:5173")}})

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Import and register blueprints
    from routes.ticket_routes import ticket_bp
    app.register_blueprint(ticket_bp)

    @app.route('/')
    def health_check():
        return jsonify({"status": "ok", "message": "AI Ticket Router backend is running."})

    return app

if __name__ == '__main__':
    app = create_app()
    # For development, debug=True is fine. For production, use a WSGI server like Gunicorn.
    app.run(debug=True, port=5001)