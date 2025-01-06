from django.core.exceptions import ValidationError

def validate_title(value):
    if not value.strip():  # Убираем пробелы и проверяем на пустую строку
        raise ValidationError("Title cannot be empty!")