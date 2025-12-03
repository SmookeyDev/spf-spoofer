"""Data models for SPF Tester."""

from src.models.config import EmailConfig, validate_email
from src.models.result import DNSInfo, SendResult

__all__ = [
    "DNSInfo",
    "EmailConfig",
    "SendResult",
    "validate_email",
]

