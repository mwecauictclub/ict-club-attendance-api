"""Validation utilities for input data."""

import re
from config.settings import (
    REG_NUMBER_PATTERN,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    VALID_COURSES,
    VALID_GENDERS,
    VALID_DEPARTMENTS,
    VALID_YEARS,
    MAX_DEPARTMENTS_PER_MEMBER
)


def normalize_reg_number(reg_number):
    """
    Normalize registration number by removing leading zeros from the last part.
    
    Examples:
        T/DEG/2020/0544 → T/DEG/2020/544
        T/DEG/2020/001 → T/DEG/2020/1
        T/DEG/2020/01 → T/DEG/2020/1
        T/DEG/2020/1 → T/DEG/2020/1 (unchanged)
    
    Args:
        reg_number: Registration number string
        
    Returns:
        str: Normalized registration number
    """
    if not reg_number or not isinstance(reg_number, str):
        return reg_number
    
    # Split by forward slash
    parts = reg_number.split('/')
    
    # If format is correct (4 parts: T, DEG/DIP, YEAR, NUMBER)
    if len(parts) == 4:
        # Remove leading zeros from the last part
        # But keep at least one digit if it's all zeros
        last_part = parts[3].lstrip('0') or '0'
        parts[3] = last_part
        return '/'.join(parts)
    
    return reg_number


def validate_reg_number(reg_number):
    """
    Validate registration number format.
    
    Format: T/(DEG|DIP)/(19|20)XX/XXX or XXXX
    Examples: T/DEG/2020/001, T/DIP/2025/1025
    
    Note: This function normalizes the reg number by removing leading zeros.
    
    Args:
        reg_number: Registration number string
        
    Returns:
        tuple: (is_valid, error_message, normalized_reg_number)
    """
    if not reg_number:
        return False, "Registration number is required", None
    
    if not isinstance(reg_number, str):
        return False, "Registration number must be a string", None
    
    # Normalize first (remove leading zeros)
    normalized = normalize_reg_number(reg_number)
    
    if not re.match(REG_NUMBER_PATTERN, normalized):
        return False, "Invalid registration number format. Examples: T/DEG/2024/001 or T/DIP/2024/1025", None
    
    return True, None, normalized


def validate_email(email):
    """
    Validate email format.
    
    Args:
        email: Email address string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    if not isinstance(email, str):
        return False, "Email must be a string"
    
    if not re.match(EMAIL_PATTERN, email.lower()):
        return False, "Invalid email format"
    
    return True, None


def validate_phone(phone):
    """
    Validate phone number format.
    
    Args:
        phone: Phone number string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"
    
    if not isinstance(phone, str):
        return False, "Phone number must be a string"
    
    if not re.match(PHONE_PATTERN, phone):
        return False, "Invalid phone number format. Should be 10-15 digits with optional +"
    
    return True, None


def validate_full_name(name):
    """
    Validate full name.
    
    Args:
        name: Full name string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name:
        return False, "Full name is required"
    
    if not isinstance(name, str):
        return False, "Full name must be a string"
    
    if len(name.strip()) < 2:
        return False, "Full name must be at least 2 characters"
    
    if len(name.strip()) > 100:
        return False, "Full name must not exceed 100 characters"
    
    return True, None


def validate_gender(gender):
    """
    Validate gender selection.
    
    Args:
        gender: Gender string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not gender:
        return False, "Gender is required"
    
    if gender not in VALID_GENDERS:
        return False, f"Gender must be one of: {', '.join(VALID_GENDERS)}"
    
    return True, None


def validate_year(year):
    """
    Validate year of study.
    
    Args:
        year: Year integer or string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if year is None or year == '':
        return False, "Year of study is required"
    
    try:
        year_int = int(year)
    except (ValueError, TypeError):
        return False, "Year of study must be a number"
    
    if year_int not in VALID_YEARS:
        return False, f"Year of study must be between 1 and 3"
    
    return True, None


def validate_course(course):
    """
    Validate course selection.
    
    Args:
        course: Course string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not course:
        return False, "Course is required"
    
    if course not in VALID_COURSES:
        return False, f"Course must be one of: {', '.join(VALID_COURSES)}"
    
    return True, None


def validate_departments(departments):
    """
    Validate department selection(s).
    
    Args:
        departments: List of department strings or comma-separated string
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not departments:
        return False, "At least one department is required"
    
    # Convert to list if string
    if isinstance(departments, str):
        departments = [d.strip() for d in departments.split(',') if d.strip()]
    
    if not isinstance(departments, list):
        return False, "Departments must be a list or comma-separated string"
    
    if len(departments) == 0:
        return False, "At least one department is required"
    
    if len(departments) > MAX_DEPARTMENTS_PER_MEMBER:
        return False, f"Maximum {MAX_DEPARTMENTS_PER_MEMBER} departments allowed"
    
    # Validate each department
    invalid_depts = [d for d in departments if d not in VALID_DEPARTMENTS]
    if invalid_depts:
        return False, f"Invalid department(s): {', '.join(invalid_depts)}"
    
    return True, None


def validate_member_data(data):
    """
    Validate all member registration data.
    
    Args:
        data: Dictionary containing member data
        
    Returns:
        tuple: (is_valid, errors_dict, normalized_data)
    """
    errors = {}
    normalized_data = data.copy()
    
    # Validate and normalize registration number
    is_valid, error, normalized_reg = validate_reg_number(data.get('reg_number'))
    if not is_valid:
        errors['reg_number'] = error
    else:
        # Update with normalized reg number
        normalized_data['reg_number'] = normalized_reg
    
    # Validate full name
    is_valid, error = validate_full_name(data.get('full_name'))
    if not is_valid:
        errors['full_name'] = error
    
    # Validate email
    is_valid, error = validate_email(data.get('email'))
    if not is_valid:
        errors['email'] = error
    
    # Validate phone
    is_valid, error = validate_phone(data.get('phone'))
    if not is_valid:
        errors['phone'] = error
    
    # Validate gender
    is_valid, error = validate_gender(data.get('gender'))
    if not is_valid:
        errors['gender'] = error
    
    # Validate year
    is_valid, error = validate_year(data.get('year_of_study'))
    if not is_valid:
        errors['year_of_study'] = error
    
    # Validate course
    is_valid, error = validate_course(data.get('course'))
    if not is_valid:
        errors['course'] = error
    
    # Validate departments
    is_valid, error = validate_departments(data.get('departments'))
    if not is_valid:
        errors['departments'] = error
    
    return len(errors) == 0, errors, normalized_data
