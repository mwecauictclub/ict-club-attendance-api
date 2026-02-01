"""Google Sheets service for data operations."""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz
from config.settings import (
    GOOGLE_CREDENTIALS,
    SPREADSHEET_ID,
    MEMBERS_SHEET,
    ATTENDANCE_SHEET,
    TIMEZONE
)


class GoogleSheetsService:
    """Service for Google Sheets operations."""
    
    def __init__(self):
        """Initialize Google Sheets connection."""
        self.client = None
        self.spreadsheet = None
        self.members_sheet = None
        self.attendance_sheet = None
        self._connect()
    
    def _connect(self):
        """Establish connection to Google Sheets."""
        try:
            # Define the scope
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Load credentials from settings dictionary
            credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                GOOGLE_CREDENTIALS,
                scope
            )
            
            # Authorize and create client
            self.client = gspread.authorize(credentials)
            
            # Open spreadsheet
            self.spreadsheet = self.client.open_by_key(SPREADSHEET_ID)
            
            # Get worksheets
            self.members_sheet = self.spreadsheet.worksheet(MEMBERS_SHEET)
            self.attendance_sheet = self.spreadsheet.worksheet(ATTENDANCE_SHEET)
            
        except Exception as e:
            raise Exception(f"Failed to connect to Google Sheets: {str(e)}")
    
    def get_member(self, reg_number):
        """
        Get member by registration number.
        
        Args:
            reg_number: Registration number
            
        Returns:
            dict: Member data or None if not found
        """
        try:
            # Get all records
            records = self.members_sheet.get_all_records()
            
            # Find member
            for record in records:
                if record.get('Reg Number') == reg_number:
                    return {
                        'reg_number': record.get('Reg Number'),
                        'full_name': record.get('Full Name'),
                        'email': record.get('Email'),
                        'phone': record.get('Phone'),
                        'gender': record.get('Gender'),
                        'year_of_study': record.get('Year of Study'),
                        'course': record.get('Course'),
                        'departments': record.get('Departments'),
                        'active': record.get('Active', 'TRUE') == 'TRUE',
                        'role': record.get('Role', 'Member'),
                        'registration_date': record.get('Registration Date')
                    }
            
            return None
            
        except Exception as e:
            raise Exception(f"Error fetching member: {str(e)}")
    
    def add_member(self, member_data):
        """
        Add new member to Members sheet.
        
        Args:
            member_data: Dictionary containing member information
            
        Returns:
            bool: True if successful
        """
        try:
            # Get timezone
            tz = pytz.timezone(TIMEZONE)
            registration_date = datetime.now(tz).strftime('%Y-%m-%d')
            
            # Prepare row data (match sheet columns)
            row = [
                member_data['reg_number'],
                member_data['full_name'],
                member_data['email'],
                member_data['phone'],
                member_data['gender'],
                member_data['year_of_study'],
                member_data['course'],
                member_data['departments'],
                'TRUE',  # Active
                member_data.get('role', 'Member'),
                registration_date
            ]
            
            # Append row
            self.members_sheet.append_row(row, value_input_option='USER_ENTERED')
            
            # Also add to attendance sheet (reg number and name only)
            attendance_row = [
                member_data['reg_number'],
                member_data['full_name']
            ]
            self.attendance_sheet.append_row(attendance_row, value_input_option='USER_ENTERED')
            
            return True
            
        except Exception as e:
            raise Exception(f"Error adding member: {str(e)}")
    
    def get_attendance_column_index(self, date_str):
        """
        Get column index for a date, create if doesn't exist.
        
        Args:
            date_str: Date string (YYYY-MM-DD)
            
        Returns:
            int: Column index (1-based)
        """
        try:
            # Get header row
            header_row = self.attendance_sheet.row_values(1)
            
            # Check if date column exists
            if date_str in header_row:
                return header_row.index(date_str) + 1  # 1-based index
            
            # Date column doesn't exist, create it
            next_col = len(header_row) + 1
            self.attendance_sheet.update_cell(1, next_col, date_str)
            
            return next_col
            
        except Exception as e:
            raise Exception(f"Error managing attendance column: {str(e)}")
    
    def mark_attendance(self, reg_number, date_str):
        """
        Mark attendance for a member on a specific date.
        
        Args:
            reg_number: Member registration number
            date_str: Date string (YYYY-MM-DD)
            
        Returns:
            bool: True if successful
        """
        try:
            # Get column index for date
            col_index = self.get_attendance_column_index(date_str)
            
            # Find member's row
            reg_numbers = self.attendance_sheet.col_values(1)  # Column A (Reg Number)
            
            try:
                row_index = reg_numbers.index(reg_number) + 1  # 1-based index
            except ValueError:
                raise Exception(f"Member {reg_number} not found in attendance sheet")
            
            # Mark as Present
            self.attendance_sheet.update_cell(row_index, col_index, 'Present')
            
            return True
            
        except Exception as e:
            raise Exception(f"Error marking attendance: {str(e)}")
    
    def get_attendance(self, reg_number, date_str):
        """
        Check if member has marked attendance for a date.
        
        Args:
            reg_number: Member registration number
            date_str: Date string (YYYY-MM-DD)
            
        Returns:
            bool: True if attendance marked, False otherwise
        """
        try:
            # Get all records
            records = self.attendance_sheet.get_all_records()
            
            # Find member's attendance
            for record in records:
                if record.get('Reg Number') == reg_number:
                    # Check if date column exists and has value
                    attendance_status = record.get(date_str, '')
                    return attendance_status == 'Present'
            
            return False
            
        except Exception as e:
            # If column doesn't exist yet, attendance is not marked
            if 'not found' in str(e).lower():
                return False
            raise Exception(f"Error checking attendance: {str(e)}")
    
    def is_member_active(self, reg_number):
        """
        Check if member is active.
        
        Args:
            reg_number: Registration number
            
        Returns:
            bool: True if active, False otherwise
        """
        member = self.get_member(reg_number)
        if not member:
            return False
        return member.get('active', False)


# Singleton instance
_sheets_service = None


def get_sheets_service():
    """
    Get singleton instance of GoogleSheetsService.
    
    Returns:
        GoogleSheetsService: Service instance
    """
    global _sheets_service
    if _sheets_service is None:
        _sheets_service = GoogleSheetsService()
    return _sheets_service
