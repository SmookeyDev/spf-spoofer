"""Email configuration model."""

import re
from dataclasses import dataclass

from src.utils.exceptions import ValidationError

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(EMAIL_REGEX.match(email))


@dataclass
class EmailConfig:
    """Email configuration for sending."""

    from_email: str
    to_email: str
    subject: str
    body: str
    from_name: str = ""
    to_name: str = ""
    html: bool = False

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        if not self.from_email:
            raise ValidationError("Sender email is required")
        if not self.to_email:
            raise ValidationError("Recipient email is required")
        if not self.subject:
            raise ValidationError("Subject is required")
        if not self.body:
            raise ValidationError("Body is required")

        if not validate_email(self.from_email):
            raise ValidationError(f"Invalid sender email: {self.from_email}")
        if not validate_email(self.to_email):
            raise ValidationError(f"Invalid recipient email: {self.to_email}")

    @property
    def from_domain(self) -> str:
        """Return the sender's domain."""
        return self.from_email.split("@")[1]

    @property
    def to_domain(self) -> str:
        """Return the recipient's domain."""
        return self.to_email.split("@")[1]

