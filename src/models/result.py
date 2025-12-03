"""Result and DNS information models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.utils.constants import ErrorType


@dataclass
class DNSInfo:
    """DNS information for a domain."""

    domain: str
    mx_records: list[tuple[int, str]] = field(default_factory=list)
    spf_record: str | None = None
    dmarc_record: str | None = None


@dataclass
class SendResult:
    """Result of an email send attempt."""

    success: bool
    error_type: ErrorType
    sender_ip: str
    mx_server: str | None = None
    spf_record: str | None = None
    dmarc_record: str | None = None
    error_message: str | None = None
    smtp_code: int | None = None
    smtp_message: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "error_type": self.error_type.value,
            "sender_ip": self.sender_ip,
            "mx_server": self.mx_server,
            "spf_record": self.spf_record,
            "dmarc_record": self.dmarc_record,
            "error_message": self.error_message,
            "smtp_code": self.smtp_code,
            "smtp_message": self.smtp_message,
            "timestamp": self.timestamp.isoformat(),
            "duration_ms": self.duration_ms,
        }

