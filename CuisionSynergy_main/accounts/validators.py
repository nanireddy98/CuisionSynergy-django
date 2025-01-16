from django.core.exceptions import ValidationError
import os


def allow_only_images(value):
    """
    Validator to allow only image files with specific extensions.
    """
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.png', '.jpg', '.jpeg', '.']

    # Check if the extension is not in the list of valid extensions
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file extension. Allowed extensions are: {', '.join(valid_extensions)}")
