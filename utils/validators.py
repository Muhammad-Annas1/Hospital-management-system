import re
from datetime import datetime, date

def validate_email(email: str) -> bool:
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email.strip()))

def validate_phone(phone: str) -> bool:
    if not phone:
        return False
    # Accepts phone numbers with 7 to 15 digits, optional + prefix, spaces or dashes
    cleaned = re.sub(r'[\s\-()]', '', phone.strip())
    return bool(re.match(r'^\+?[0-9]{7,15}$', cleaned))

def validate_dob(dob_str: str) -> tuple[bool, str]:
    """Validates that DOB format is YYYY-MM-DD and is not in the future."""
    try:
        if isinstance(dob_str, date):
            dob_date = dob_str
        else:
            dob_date = datetime.strptime(str(dob_str), "%Y-%m-%d").date()
        
        if dob_date > date.today():
            return False, "Date of birth cannot be in the future."
        return True, ""
    except ValueError:
        return False, "Invalid date format. Expected YYYY-MM-DD."

def calculate_age(dob: date | str) -> int:
    if isinstance(dob, str):
        dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
    else:
        dob_date = dob
    today = date.today()
    return today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))

def validate_non_negative(val: float | int, field_name: str) -> tuple[bool, str]:
    if val is None or val < 0:
        return False, f"{field_name} cannot be negative."
    return True, ""
