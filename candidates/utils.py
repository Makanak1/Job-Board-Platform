import os
from django.core.exceptions import ValidationError
from django.conf import settings

def validate_file_size(file, max_size_mb=5):
    """
    Validate file size
    """
    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
    if file.size > max_size:
        raise ValidationError(f"File size cannot exceed {max_size_mb}MB")

def validate_file_extension(file, allowed_extensions):
    """
    Validate file extension
    """
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f"File type not supported. Allowed types: {', '.join(allowed_extensions)}")

def get_file_extension(filename):
    """
    Get file extension from filename
    """
    return os.path.splitext(filename)[1].lower()

def generate_unique_filename(instance, filename):
    """
    Generate unique filename with timestamp
    """
    import uuid
    from datetime import datetime
    
    ext = get_file_extension(filename)
    unique_filename = f"{uuid.uuid4().hex}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
    return unique_filename