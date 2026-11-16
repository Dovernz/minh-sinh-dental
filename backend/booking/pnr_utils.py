import secrets
from django.apps import apps
from django.db.models import Q

SAFE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _code_exists_in_booking(code: str) -> bool:
    """Check if code exists in Booking model (pnr_code or group_code)."""
    if not apps.ready:
        return False
    try:
        booking_model = None
        for model in apps.get_models():
            if model.__name__ == "Booking":
                booking_model = model
                break
        if booking_model is not None:
            return booking_model.objects.filter(
                Q(pnr_code=code) | Q(group_code=code)
            ).exists()
    except Exception:
        pass
    return False


def generate_pnr_code(prefix: str = "", length: int = 6) -> str:
    """
    Generates a random uppercase alphanumeric PNR code of given length.
    If prefix is provided, total length is length (prefix + remaining chars).
    Ensures uniqueness against Booking model if Django apps are ready.
    """
    prefix = (prefix or "").strip().upper()
    remaining_length = max(0, length - len(prefix))

    while True:
        random_chars = "".join(
            secrets.choice(SAFE_ALPHABET) for _ in range(remaining_length)
        )
        code = f"{prefix}{random_chars}"

        if not _code_exists_in_booking(code):
            return code


def validate_pnr_code(code: str) -> bool:
    """
    Checks if string is 6 characters alphanumeric, uppercase.
    """
    if not isinstance(code, str):
        return False
    return len(code) == 6 and code.isalnum() and code.isupper()


def format_pnr(code: str) -> str:
    """
    Uppercases and strips whitespace.
    """
    if not isinstance(code, str):
        return ""
    return code.strip().upper()