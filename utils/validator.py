import re
import os
from core.exceptions import ValidationError

class Validator:
    """Utility class providing static methods for input validation."""

    ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}
    EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    @staticmethod
    def validate_non_empty(value: str, field_name: str) -> str:
        """Ensures that a string is non-empty and non-whitespace."""
        if not value or not str(value).strip():
            raise ValidationError(f"The field '{field_name}' cannot be empty.")
        return value.strip()

    @staticmethod
    def validate_email(email: str) -> str:
        """Validates standard email formatting."""
        email = Validator.validate_non_empty(email, "Email")
        if not re.match(Validator.EMAIL_REGEX, email):
            raise ValidationError("Please enter a valid email address.")
        return email

    @staticmethod
    def validate_contact_no(contact_no: str) -> str:
        """Validates phone number format."""
        contact_no = Validator.validate_non_empty(contact_no, "Contact Number")
        cleaned_no = re.sub(r'[\s\-\(\)]', '', contact_no)
        if not cleaned_no.isdigit() or len(cleaned_no) < 7 or len(cleaned_no) > 15:
            raise ValidationError("Please enter a valid contact phone number (7-15 digits).")
        return cleaned_no

    @staticmethod
    def validate_image_file(file_path: str) -> str:
        """Validates photo existence and allowed image extension."""
        if not file_path or not os.path.exists(file_path):
            raise ValidationError("A valid photo upload is required.")
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in Validator.ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(f"Invalid image format. Allowed formats: {', '.join(Validator.ALLOWED_IMAGE_EXTENSIONS)}")
        return file_path