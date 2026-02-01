"""Error handlers for the API."""

from flask import jsonify
from utils.helpers import format_error_response


def register_error_handlers(app):
    """Register error handlers with Flask app."""
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify(format_error_response(
            'NOT_FOUND',
            'The requested resource was not found',
            str(error)
        )), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 errors."""
        return jsonify(format_error_response(
            'METHOD_NOT_ALLOWED',
            'The method is not allowed for this endpoint',
            str(error)
        )), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        return jsonify(format_error_response(
            'INTERNAL_ERROR',
            'An internal server error occurred',
            str(error)
        )), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle all unhandled exceptions."""
        return jsonify(format_error_response(
            'UNKNOWN_ERROR',
            'An unexpected error occurred',
            str(error)
        )), 500
