"""API routes for the attendance system."""

from flask import Blueprint, request, jsonify, render_template
from services import get_member_service, get_attendance_service
from utils.validators import validate_reg_number
from utils.helpers import format_error_response, format_success_response
from utils.session_manager import get_current_session_info

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize services
member_service = get_member_service()
attendance_service = get_attendance_service()


@api_bp.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@api_bp.route('/register')
def register_page():
    """Registration page."""
    return render_template('register.html')


@api_bp.route('/attendance')
def attendance_page():
    """Attendance marking page."""
    return render_template('attendance.html')


@api_bp.route('/api/check-member', methods=['POST'])
def check_member():
    """
    Check if a member exists in the database.
    
    Request Body:
        {
            "reg_number": "T/DEG/2020/001"
        }
    
    Response:
        {
            "success": true,
            "exists": true,
            "data": {...member data...}
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'reg_number' not in data:
            return jsonify(format_error_response(
                'INVALID_REQUEST',
                'Registration number is required'
            )), 400
        
        reg_number = data['reg_number'].strip()
        
        # Validate format and normalize
        is_valid, error, normalized_reg = validate_reg_number(reg_number)
        if not is_valid:
            return jsonify(format_error_response(
                'INVALID_REG_NUMBER',
                error
            )), 400
        
        # Check if exists (using normalized reg number)
        member = member_service.get_member_info(normalized_reg)
        
        if member:
            return jsonify(format_success_response(
                data={
                    'exists': True,
                    'member': member
                }
            )), 200
        else:
            return jsonify(format_success_response(
                data={
                    'exists': False
                },
                message='Member not found. Would you like to register?'
            )), 200
        
    except Exception as e:
        return jsonify(format_error_response(
            'UNKNOWN_ERROR',
            'An unexpected error occurred',
            str(e)
        )), 500


@api_bp.route('/api/register', methods=['POST'])
def register():
    """
    Register a new member.
    
    Request Body:
        {
            "reg_number": "e.g T/DEG/2025/0001",
            "full_name": "e.g Johnson Mwakyusa",
            "email": "john@gmail.com",
            "phone": "+255XXXXXXXXX",
            "gender": "e.g Male",
            "year_of_study": 2,
            "course": "ICT",
            "departments": ["Programming", "AI & Machine Learning"]
        }
    
    Response:
        {
            "success": true,
            "message": "Registration successful",
            "data": {...}
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(format_error_response(
                'INVALID_REQUEST',
                'Request body is required'
            )), 400
        
        # Register member
        success, result = member_service.register_member(data)
        
        if success:
            return jsonify(format_success_response(
                data=result,
                message='Registration successful'
            )), 201
        else:
            # Registration failed
            error = result
            status_code = 409 if error['code'] == 'DUPLICATE_REGISTRATION' else 400
            return jsonify(format_error_response(
                error['code'],
                error['message'],
                error.get('details')
            )), status_code
        
    except Exception as e:
        return jsonify(format_error_response(
            'UNKNOWN_ERROR',
            'An unexpected error occurred',
            str(e)
        )), 500


@api_bp.route('/api/mark-attendance', methods=['POST'])
def mark_attendance():
    """
    Mark attendance for a member.
    
    Request Body:
        {
            "reg_number": "T/DEG/2020/001",
            "session_code": "NET30JAN"
        }
    
    Response:
        {
            "success": true,
            "message": "Attendance marked successfully",
            "data": {...}
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify(format_error_response(
                'INVALID_REQUEST',
                'Request body is required'
            )), 400
        
        # Validate required fields
        if 'reg_number' not in data or 'session_code' not in data:
            return jsonify(format_error_response(
                'INVALID_REQUEST',
                'Registration number and session code are required'
            )), 400
        
        reg_number = data['reg_number'].strip()
        session_code = data['session_code'].strip()
        
        # Validate and normalize reg number format
        is_valid, error, normalized_reg = validate_reg_number(reg_number)
        if not is_valid:
            return jsonify(format_error_response(
                'INVALID_REG_NUMBER',
                error
            )), 400
        
        # Mark attendance (using normalized reg number)
        success, result = attendance_service.mark_attendance(normalized_reg, session_code)
        
        if success:
            return jsonify(format_success_response(
                data=result,
                message='Attendance marked successfully'
            )), 200
        else:
            # Attendance marking failed
            error = result
            status_codes = {
                'MEMBER_NOT_FOUND': 404,
                'MEMBER_INACTIVE': 403,
                'TIME_WINDOW_CLOSED': 400,
                'INVALID_SESSION_CODE': 400,
                'DUPLICATE_ATTENDANCE': 409
            }
            status_code = status_codes.get(error['code'], 400)
            
            return jsonify(format_error_response(
                error['code'],
                error['message'],
                error.get('details')
            )), status_code
        
    except Exception as e:
        return jsonify(format_error_response(
            'UNKNOWN_ERROR',
            'An unexpected error occurred',
            str(e)
        )), 500


@api_bp.route('/api/session-info', methods=['GET'])
def session_info():
    """
    Get current session information.
    
    Response:
        {
            "success": true,
            "data": {
                "has_session": true,
                "session": {...session details...}
            }
        }
    """
    try:
        info = get_current_session_info()
        return jsonify(format_success_response(data=info)), 200
    
    except Exception as e:
        return jsonify(format_error_response(
            'UNKNOWN_ERROR',
            'An unexpected error occurred',
            str(e)
        )), 500


@api_bp.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint.
    
    Response:
        {
            "status": "healthy",
            "timestamp": "2026-01-30T14:30:00+03:00",
            "version": "1.0"
        }
    """
    from datetime import datetime
    import pytz
    from config.settings import TIMEZONE
    
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    
    # Try to connect to Google Sheets
    try:
        from services import get_sheets_service
        sheets = get_sheets_service()
        sheets_status = "connected"
    except:
        sheets_status = "error"
    
    return jsonify({
        'status': 'healthy' if sheets_status == 'connected' else 'degraded',
        'timestamp': now.isoformat(),
        'version': '1.0',
        'services': {
            'google_sheets': sheets_status
        }
    }), 200
