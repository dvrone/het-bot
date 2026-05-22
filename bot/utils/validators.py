def validate_account_number(account_number: str, user_type: str) -> bool:
    """
    Validate account number based on user type.
    - individual (jismoniy): exactly 7 digits
    - legal (yuridik): exactly 6 digits
    """
    digits = account_number.strip()
    if not digits.isdigit():
        return False
    if user_type == "individual":
        return len(digits) == 7
    elif user_type == "legal":
        return len(digits) == 6
    return False
