 # api/helpers/Validate.py
import re

def validate_email(email: str) -> bool:
    """
    Validate email address using a regular expression.
    Returns True if the email is valid, otherwise False.
    """
    # Email regex pattern
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    # Match email to the pattern
    return bool(re.match(email_pattern, email))

def validate_password(password: str) -> bool:
    """
    Validate password with the following criteria:
    - At least 10 characters long
    - Contains at least one letter
    - Contains at least one special character or one digit
    Returns True if the password meets the criteria, otherwise False.
    """
    if len(password) < 10:
        return False

    # Kiểm tra có ít nhất một ký tự chữ cái
    if not re.search(r'[A-Za-z]', password):
        return False
    
    # Kiểm tra có ít nhất một ký tự đặc biệt hoặc một con số
    if not re.search(r'[\W_0-9]', password):
        return False
    
    return True
