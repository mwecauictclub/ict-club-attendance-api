"""Attendance service for attendance-related operations."""

from services.sheets_service import get_sheets_service
from services.member_service import get_member_service
from utils.session_manager import (
    get_current_friday_date,
    is_within_time_window,
    validate_session_code
)


class AttendanceService:
    """Service for attendance operations."""
    
    def __init__(self):
        """Initialize attendance service."""
        self.sheets = get_sheets_service()
        self.member_service = get_member_service()
    
    def mark_attendance(self, reg_number, session_code):
        """
        Mark attendance for a member.
        
        Args:
            reg_number: Member registration number
            session_code: Session code provided by leader
            
        Returns:
            tuple: (success, error_or_data)
        """
        # 1. Check if member exists
        if not self.member_service.check_member_exists(reg_number):
            return False, {
                'code': 'MEMBER_NOT_FOUND',
                'message': 'Member not found',
                'details': 'Registration number not in database. Please register first.'
            }
        
        # 2. Check if member is active
        if not self.member_service.is_member_active(reg_number):
            return False, {
                'code': 'MEMBER_INACTIVE',
                'message': 'Your membership is inactive',
                'details': 'Please contact club administration'
            }
        
        # 3. Check time window
        is_valid_time, reason = is_within_time_window()
        if not is_valid_time:
            return False, {
                'code': 'TIME_WINDOW_CLOSED',
                'message': 'Attendance marking window closed',
                'details': reason
            }
        
        # 4. Get current Friday date
        friday_date = get_current_friday_date()
        date_str = friday_date.strftime('%Y-%m-%d')
        
        # 5. Validate session code
        code_valid, error, session = validate_session_code(session_code, date_str)
        if not code_valid:
            return False, {
                'code': 'INVALID_SESSION_CODE',
                'message': error or 'Invalid session code',
                'details': 'The session code provided is incorrect'
            }
        
        # 6. Check if already marked attendance
        if self.has_marked_attendance(reg_number, date_str):
            return False, {
                'code': 'DUPLICATE_ATTENDANCE',
                'message': 'Attendance already marked',
                'details': f'You have already marked attendance for {date_str}'
            }
        
        # 7. Mark attendance
        try:
            self.sheets.mark_attendance(reg_number, date_str)
            
            # Get member info for response
            member = self.member_service.get_member_info(reg_number)
            
            return True, {
                'reg_number': reg_number,
                'full_name': member['full_name'],
                'session_date': date_str,
                'department': session['department'],
                'message': 'Attendance marked successfully'
            }
        except Exception as e:
            return False, {
                'code': 'SHEETS_API_ERROR',
                'message': 'Database error',
                'details': str(e)
            }
    
    def has_marked_attendance(self, reg_number, date_str):
        """
        Check if member has already marked attendance for a date.
        
        Args:
            reg_number: Registration number
            date_str: Date string (YYYY-MM-DD)
            
        Returns:
            bool: True if already marked
        """
        return self.sheets.get_attendance(reg_number, date_str)


# Singleton instance
_attendance_service = None


def get_attendance_service():
    """
    Get singleton instance of AttendanceService.
    
    Returns:
        AttendanceService: Service instance
    """
    global _attendance_service
    if _attendance_service is None:
        _attendance_service = AttendanceService()
    return _attendance_service
