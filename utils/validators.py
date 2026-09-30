import re
from datetime import datetime

EMAIL_REGEX = re.compile(r"^[\w\.-]+@([\w\.-]+\.)+[\w-]{2,4}$")

def validate_email(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_positive_number(val) -> tuple[bool, float]:
    try:
        num = float(val)
        if num > 0:
            return True, round(num, 2)
        return False, 0.0
    except (ValueError, TypeError):
        return False, 0.0

def validate_non_negative_number(val) -> tuple[bool, float]:
    try:
        num = float(val)
        if num >= 0:
            return True, round(num, 2)
        return False, 0.0
    except (ValueError, TypeError):
        return False, 0.0

def parse_date(date_str: str):
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            pass
    return None
