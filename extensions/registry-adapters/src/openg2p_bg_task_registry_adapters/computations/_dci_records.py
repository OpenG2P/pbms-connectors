"""Value helpers for flattening a rendered DCI reg_record onto column names."""

from datetime import date


def age_from_birth_date(value):
    if not value:
        return None
    if isinstance(value, str):
        try:
            value = date.fromisoformat(value[:10])
        except ValueError:
            return None
    today = date.today()
    return (
        today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    )


def as_bool(value):
    if isinstance(value, bool):
        return value
    if value in (None, ""):
        return None
    return str(value).lower() in ("true", "1")


def as_int(value):
    if value in (None, ""):
        return None
    return int(value)


def text(value):
    return value if value not in (None, "") else None


def code(value):
    """Undo the template's display casing: "Assessed disabled" -> "ASSESSED_DISABLED"."""
    if value in (None, ""):
        return None
    return str(value).strip().upper().replace(" ", "_")


def identifier_of_type(identifiers, identifier_type: str):
    for item in identifiers or []:
        if isinstance(item, dict) and item.get("identifier_type") == identifier_type:
            return text(item.get("identifier_value"))
    return None
