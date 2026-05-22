import re
from typing import Optional


def normalize_phone(raw: str) -> Optional[str]:
    """Normalize and validate Uzbek phone numbers."""
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("998") and len(digits) == 12:
        return f"+{digits}"
    if len(digits) == 9:
        return f"+998{digits}"
    if len(digits) == 10 and digits.startswith("0"):
        return f"+998{digits[1:]}"
    return None
