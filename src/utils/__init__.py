"""Utility modules for SPF Tester."""

from src.utils.constants import (
    DEFAULT_TIMEOUT,
    DNS_TIMEOUT,
    SMTP_PORT,
    SMTP_SUBMISSION_PORT,
    SMTPS_PORT,
    USER_AGENT,
    VERSION,
    ErrorType,
    OutputFormat,
)
from src.utils.exceptions import (
    ConfigError,
    DNSError,
    SMTPError,
    SPFTesterError,
    ValidationError,
)

__all__ = [
    "DEFAULT_TIMEOUT",
    "DNS_TIMEOUT",
    "SMTP_PORT",
    "SMTP_SUBMISSION_PORT",
    "SMTPS_PORT",
    "USER_AGENT",
    "VERSION",
    "ErrorType",
    "OutputFormat",
    "ConfigError",
    "DNSError",
    "SMTPError",
    "SPFTesterError",
    "ValidationError",
]

