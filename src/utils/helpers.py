"""Helper utilities."""


def format_departments(departments):
    """
    Format department list as comma-separated string.
    
    Args:
        departments: List of department names or comma-separated string
        
    Returns:
        str: Comma-separated department names
    """
    if isinstance(departments, str):
        # Already a string, just clean it up
        return ', '.join([d.strip() for d in departments.split(',') if d.strip()])
    elif isinstance(departments, list):
        return ', '.join(departments)
    else:
        return ''


def parse_departments(departments_str):
    """
    Parse comma-separated department string into list.
    
    Args:
        departments_str: Comma-separated string
        
    Returns:
        list: List of department names
    """
    if not departments_str:
        return []
    
    if isinstance(departments_str, list):
        return departments_str
    
    return [d.strip() for d in departments_str.split(',') if d.strip()]


def format_error_response(code, message, details=None):
    """
    Format standard error response.
    
    Args:
        code: Error code string
        message: Human-readable error message
        details: Additional error details (optional)
        
    Returns:
        dict: Formatted error response
    """
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }
    
    if details:
        response['error']['details'] = details
    
    return response


def format_success_response(data=None, message=None):
    """
    Format standard success response.
    
    Args:
        data: Response data (optional)
        message: Success message (optional)
        
    Returns:
        dict: Formatted success response
    """
    response = {'success': True}
    
    if message:
        response['message'] = message
    
    if data:
        response['data'] = data
    
    return response
