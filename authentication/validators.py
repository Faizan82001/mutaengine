import re
from rest_framework import serializers

def validate_password(password, username, email):
    # Check if the password contains the username or email
    if username.lower() in password.lower() or email.lower() in password.lower():
        raise serializers.ValidationError("Password should not contain your username or email.")

    # Check if the password length is between 8 and 16 characters
    if len(password) < 8 or len(password) > 16:
        raise serializers.ValidationError("Password must be between 8 and 16 characters.")

    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        raise serializers.ValidationError("Password must contain at least one uppercase letter.")

    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        raise serializers.ValidationError("Password must contain at least one lowercase letter.")

    # Check for at least one digit
    if not re.search(r'\d', password):
        raise serializers.ValidationError("Password must contain at least one digit.")

    # Check for at least one special character
    if not re.search(r'[\W_]', password):  # \W is for non-word characters, including special characters
        raise serializers.ValidationError("Password must contain at least one special character.")
    
    return password
