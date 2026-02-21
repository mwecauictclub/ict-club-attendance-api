"""Main Flask application for MWECAU ICT Club Attendance System."""

import sys
import os

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_cors import CORS
from api import api_bp, register_error_handlers
from config.settings import SECRET_KEY, DEBUG

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = SECRET_KEY
app.config['DEBUG'] = DEBUG
app.config['JSON_SORT_KEYS'] = False

# Enable CORS
CORS(app)

# Register blueprints
app.register_blueprint(api_bp)

# Register error handlers
register_error_handlers(app)


if __name__ == '__main__':
    # Run the application
    app.run(
