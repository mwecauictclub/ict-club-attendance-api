"""Session management utilities."""

from datetime import datetime, timedelta
import pytz
from config.settings import (
    TIMEZONE,
    ATTENDANCE_START_HOUR,
    ATTENDANCE_END_HOUR,
    ATTENDANCE_END_DAY_OFFSET
)
from config.sessions import get_session, get_current_friday_session


def get_current_datetime():
    """
    Get current datetime in configured timezone.
    
    Returns:
        datetime: Current datetime with timezone
    """
    tz = pytz.timezone(TIMEZONE)
    return datetime.now(tz)


def get_current_friday_date():
    """
    Get the date of current Friday (if today) or most recent Friday.
    
    Returns:
        date: Friday date or None if no recent Friday
    """
    now = get_current_datetime()
    
    # If today is Friday
    if now.weekday() == 4:  # Friday is 4
        return now.date()
    
    # If today is Saturday (day after Friday)
    if now.weekday() == 5:  # Saturday is 5
        # Return yesterday (Friday)
        return (now - timedelta(days=1)).date()
    
    # Otherwise, find last Friday
    days_since_friday = (now.weekday() - 4) % 7
    if days_since_friday == 0:
        return now.date()
    
    last_friday = now - timedelta(days=days_since_friday)
    return last_friday.date()


def is_within_time_window(current_datetime=None):
    """
    Check if current time is within attendance marking window.
    
    Window: Friday 13:00 → Saturday 00:00
    
    Args:
        current_datetime: datetime to check (default: now)
        
    Returns:
        tuple: (is_within, reason)
    """
    if current_datetime is None:
        current_datetime = get_current_datetime()
    
    # Get current day and time
    current_day = current_datetime.weekday()  # 0=Monday, 4=Friday, 5=Saturday
    current_time = current_datetime.time()
    
    # Friday (day 4): From 13:00 onwards
    if current_day == 4:
        start_time = datetime.strptime(f"{ATTENDANCE_START_HOUR}:00", "%H:%M").time()
        if current_time >= start_time:
            return True, None
        else:
            return False, f"Attendance marking starts at {ATTENDANCE_START_HOUR}:00 on Friday"
    
    # Saturday (day 5): Until 00:00 (which is start of day)
    elif current_day == 5:
        end_time = datetime.strptime(f"{ATTENDANCE_END_HOUR:02d}:00", "%H:%M").time()
        # Since ATTENDANCE_END_HOUR is 0 (midnight), this means any time on Saturday is past window
        return False, "Attendance marking window closed (ended at Saturday 00:00)"
    
    # Other days
    else:
        return False, "Attendance can only be marked from Friday 13:00 to Saturday 00:00"


def validate_session_code(session_code, date_str=None):
    """
    Validate session code against expected code for the date.
    
    Args:
        session_code: Code to validate
        date_str: Date string (YYYY-MM-DD), defaults to current Friday
        
    Returns:
        tuple: (is_valid, error_message, session_data)
    """
    if not session_code:
        return False, "Session code is required", None
    
    # Get date if not provided
    if date_str is None:
        friday_date = get_current_friday_date()
        date_str = friday_date.strftime('%Y-%m-%d')
    
    # Get expected session for this date
    session = get_session(date_str)
    
    if not session:
        return False, f"No session scheduled for {date_str}", None
    
    # Validate code
    if session_code.upper() != session['code'].upper():
        return False, "Invalid session code", None
    
    return True, None, session


def get_session_info_for_date(date_str):
    """
    Get session information for a specific date.
    
    Args:
        date_str: Date string (YYYY-MM-DD)
        
    Returns:
        dict: Session info or None
    """
    session = get_session(date_str)
    if session:
        session = session.copy()
        session['date'] = date_str
    return session


def get_current_session_info():
    """
    Get current session information with time window status.
    
    Returns:
        dict: Session info with window status
    """
    now = get_current_datetime()
    friday_date = get_current_friday_date()
    date_str = friday_date.strftime('%Y-%m-%d')
    
    session = get_session(date_str)
    
    if not session:
        return {
            'has_session': False,
            'message': 'No session scheduled for this week'
        }
    
    # Check time window
    is_active, reason = is_within_time_window(now)
    
    # Calculate time remaining if active
    time_remaining = None
    if is_active:
        # End time is Saturday 00:00
        saturday = friday_date + timedelta(days=1)
        end_datetime = datetime.combine(saturday, datetime.min.time())
        end_datetime = pytz.timezone(TIMEZONE).localize(end_datetime)
        
        remaining = end_datetime - now
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        time_remaining = f"{hours}h {minutes}m"
    
    return {
        'has_session': True,
        'session': {
            'date': date_str,
            'day': 'Friday',
            'department': session['department'],
            'description': session['description'],
            'time': '13:30 - 15:30 EAT',
            'attendance_window': {
                'start': f"{date_str}T{ATTENDANCE_START_HOUR:02d}:00:00+03:00",
                'end': f"{(friday_date + timedelta(days=1)).strftime('%Y-%m-%d')}T{ATTENDANCE_END_HOUR:02d}:00:00+03:00",
                'is_active': is_active,
                'reason': reason,
                'time_remaining': time_remaining
            }
        }
    }
