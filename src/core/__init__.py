"""Core functionality for SPF Tester."""

from src.core.dns import (
    get_dmarc_record,
    get_dns_info,
    get_mx_records,
    get_spf_record,
)
from src.core.sender import get_public_ip, send_direct

__all__ = [
    "get_dmarc_record",
    "get_dns_info",
    "get_mx_records",
    "get_public_ip",
    "get_spf_record",
    "send_direct",
]

