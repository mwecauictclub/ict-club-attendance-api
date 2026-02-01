"""Application settings and configuration."""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Flask Configuration
SECRET_KEY = 'mwecau-ict-club-secret-key-2026'
DEBUG = False

# Google Service Account Credentials (stored directly)
GOOGLE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "xxxx",
    "private_key_id": "xxxx",
    "private_key": "xxxx",
    "client_email": "xxxx",
    "client_id": "xxxx",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/mwecau-ict-attendance-sa%40mwecau-ict-attendance.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Google Sheets Configuration
SPREADSHEET_ID = 'xxxx'
MEMBERS_SHEET = 'xxxx'
ATTENDANCE_SHEET = 'xxxx'
REPORTS_SHEET = 'xxxx'

# Attendance Window Settings
ATTENDANCE_START_HOUR = 13  # 13:00 (1:00 PM)
ATTENDANCE_END_DAY_OFFSET = 1  # Next day (Saturday)
ATTENDANCE_END_HOUR = 0  # 00:00 (Midnight)

# Timezone
TIMEZONE = 'Africa/Dar_es_Salaam'  # EAT (UTC+3)

# Validation Patterns
REG_NUMBER_PATTERN = r'^T\/(DEG|DIP)\/(19|20)\d{2}\/\d{1,4}$'  # 1 to 4 digits at end
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_PATTERN = r'^\+?[0-9]{10,15}$'

# Valid Options
VALID_COURSES = ['ICT', 'CS']
VALID_GENDERS = ['Male', 'Female', 'Other']
VALID_DEPARTMENTS = [
    'Cybersecurity',
    'Programming',
    'Networking',
    'Computer Maintenance',
    'Graphic Design',
    'AI & Machine Learning'
]
VALID_YEARS = [1, 2, 3]

# Application Settings
MAX_DEPARTMENTS_PER_MEMBER = 6
MIN_YEAR = 1
MAX_YEAR = 3
