from datetime import datetime

def get_current_time():
    """
    Returns the current time in ISO 8601 format.
    """
    return datetime.now().isoformat()