"""Session codes and schedule configuration."""

from datetime import datetime, timedelta
import pytz
from .settings import TIMEZONE

# Hardcoded session codes for each Friday
SESSIONS = {
    "2026-01-30": {
        "department": "Networking",
        "code": "NET30JAN",
        "description": "Design and implementation of robust networks"
    },
    "2026-02-06": {
        "department": "Computer Maintenance",
        "code": "COMP06FEB",
        "description": "Hardware/software troubleshooting and repair"
    },
    "2026-02-13": {
        "department": "Graphic Design",
        "code": "GRAPH13FEB",
        "description": "Visual design using Adobe tools & Canva"
    },
    "2026-02-20": {
        "department": "Artificial Intelligence (AI) & Machine Learning",
        "code": "AI20FEB",
        "description": "AI-driven automation and prototyping"
    },
    "2026-02-27": {
        "department": "Cybersecurity",
        "code": "CYBER27FEB",
        "description": "Ethical hacking, digital forensics, and secure computing"
    },
    "2026-03-06": {
        "department": "Programming",
        "code": "PROG06MAR",
        "description": "Software development in Python, JavaScript, PHP, etc."
    },
    "2026-03-13": {
        "department": "Networking",
        "code": "NET13MAR",
        "description": "Design and implementation of robust networks"
    },
    "2026-03-20": {
        "department": "Computer Maintenance",
        "code": "COMP20MAR",
        "description": "Hardware/software troubleshooting and repair"
    },
    "2026-03-27": {
        "department": "Graphic Design",
        "code": "GRAPH27MAR",
        "description": "Visual design using Adobe tools & Canva"
    },
    "2026-04-03": {
        "department": "Artificial Intelligence (AI) & Machine Learning",
        "code": "AI03APR",
        "description": "AI-driven automation and prototyping"
    },
}



def get_session(date_str):
    """
    Get session by date string (YYYY-MM-DD).

    Args:
        date_str: Date string in format YYYY-MM-DD

    Returns:
        dict: Session details or None if not found
    """
    return SESSIONS.get(date_str)


def get_current_friday_session():
    """
    Get current or upcoming Friday session based on current time.

    Returns:
        dict: Session details with 'date' key added, or None
    """
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)

    # Find current Friday or next Friday
    days_until_friday = (4 - now.weekday()) % 7  # Friday is 4
    if days_until_friday == 0:
        # Today is Friday
        friday_date = now.date()
    else:
        # Get next Friday
        friday_date = (now + timedelta(days=days_until_friday)).date()

    date_str = friday_date.strftime('%Y-%m-%d')
    session = SESSIONS.get(date_str)

    if session:
        session = session.copy()
        session['date'] = date_str

    return session


def get_next_session_after(date_str):
    """
    Get the next session after a given date.

    Args:
        date_str: Date string in format YYYY-MM-DD

    Returns:
        dict: Next session details with 'date' key, or None
    """
    dates = sorted(SESSIONS.keys())
    for d in dates:
        if d > date_str:
            session = SESSIONS[d].copy()
            session['date'] = d
            return session
    return None
