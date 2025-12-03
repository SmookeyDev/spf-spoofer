"""Constants and enumerations for SPF Tester."""

from enum import Enum


class ErrorType(str, Enum):
    """Types of sending errors."""

    SUCCESS = "SUCCESS"
    DNS_ERROR = "DNS_ERROR"
    NO_MX_RECORDS = "NO_MX_RECORDS"
    CONNECTION_FAILED = "CONNECTION_FAILED"
    TIMEOUT = "TIMEOUT"
    NO_PTR_RECORD = "NO_PTR_RECORD"
    SPF_FAIL = "SPF_FAIL"
    DKIM_FAIL = "DKIM_FAIL"
    DMARC_FAIL = "DMARC_FAIL"
    SPAM_DETECTED = "SPAM_DETECTED"
    SENDER_REFUSED = "SENDER_REFUSED"
    RECIPIENT_REFUSED = "RECIPIENT_REFUSED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    REJECTED = "REJECTED"
    ALL_MX_FAILED = "ALL_MX_FAILED"
    UNKNOWN = "UNKNOWN"


class OutputFormat(str, Enum):
    """Output formats."""

    TEXT = "text"
    JSON = "json"
    QUIET = "quiet"


# Default SMTP ports
SMTP_PORT = 25
SMTP_SUBMISSION_PORT = 587
SMTPS_PORT = 465

# Timeouts (seconds)
DEFAULT_TIMEOUT = 30
DNS_TIMEOUT = 10

# Version info
VERSION = "1.0.0"
USER_AGENT = f"SPFSpoofer/{VERSION}"

