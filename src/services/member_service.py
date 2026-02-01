"""Member service for member-related operations."""

from services.sheets_service import get_sheets_service
from utils.validators import validate_member_data
from utils.helpers import format_departments


class MemberService:
    """Service for member operations."""
    
    def __init__(self):
        """Initialize member service."""
        self.sheets = get_sheets_service()
    
    def check_member_exists(self, reg_number):
        """
        Check if member exists in database.
        
        Args:
            reg_number: Registration number
            
        Returns:
            bool: True if exists, False otherwise
        """
        member = self.sheets.get_member(reg_number)
        return member is not None
    
    def get_member_info(self, reg_number):
        """
        Get member information.
        
        Args:
            reg_number: Registration number
            
        Returns:
            dict: Member information or None
        """
        return self.sheets.get_member(reg_number)
    
    def is_member_active(self, reg_number):
        """
        Check if member is active.
        
        Args:
            reg_number: Registration number
            
        Returns:
            bool: True if active
        """
        return self.sheets.is_member_active(reg_number)
    
    def register_member(self, member_data):
        """
        Register a new member.
        
        Args:
            member_data: Dictionary with member information
            
        Returns:
            tuple: (success, error_or_data)
        """
        # Validate data and get normalized version
        is_valid, errors, normalized_data = validate_member_data(member_data)
        if not is_valid:
            return False, {'code': 'VALIDATION_ERROR', 'message': 'Invalid input data', 'details': errors}
        
        # Use normalized data (with leading zeros removed)
        # Check if already exists
        if self.check_member_exists(normalized_data['reg_number']):
            return False, {'code': 'DUPLICATE_REGISTRATION', 'message': 'Registration number already exists'}
        
        # Format departments
        normalized_data['departments'] = format_departments(normalized_data['departments'])
        
        # Add to database
        try:
            self.sheets.add_member(normalized_data)
            
            return True, {
                'reg_number': normalized_data['reg_number'],
                'full_name': normalized_data['full_name'],
                'message': 'Registration successful'
            }
        except Exception as e:
            return False, {'code': 'SHEETS_API_ERROR', 'message': str(e)}


# Singleton instance
_member_service = None


def get_member_service():
    """
    Get singleton instance of MemberService.
    
    Returns:
        MemberService: Service instance
    """
    global _member_service
    if _member_service is None:
        _member_service = MemberService()
    return _member_service
