import re
from typing import Literal

from email_validator import EmailNotValidError, validate_email


IdentifierKind = Literal["email", "phone"]
_PHONE_SEPARATORS = re.compile(r"[\s().-]+")


def normalize_email(email: object) -> str:
    return str(email).strip().casefold()


def normalize_vietnamese_phone(phone_number: object) -> str:
    compact = _PHONE_SEPARATORS.sub("", str(phone_number).strip())
    if re.fullmatch(r"0\d{9}", compact):
        return f"+84{compact[1:]}"
    if re.fullmatch(r"84\d{9}", compact):
        return f"+{compact}"
    if re.fullmatch(r"\+84\d{9}", compact):
        return compact
    raise ValueError("Enter a valid Vietnamese phone number")


def normalize_login_identifier(identifier: object) -> tuple[IdentifierKind, str]:
    value = str(identifier).strip()
    if "@" in value:
        try:
            normalized = validate_email(
                value,
                check_deliverability=False,
            ).normalized
        except EmailNotValidError as error:
            raise ValueError(
                "Enter a valid email address or Vietnamese phone number"
            ) from error
        return "email", normalize_email(normalized)
    return "phone", normalize_vietnamese_phone(value)


def mask_phone_number(phone_number: str | None) -> str | None:
    if not phone_number:
        return None
    return f"{phone_number[:3]}•••••{phone_number[-3:]}"
