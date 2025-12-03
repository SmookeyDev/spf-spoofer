"""
SPF Spoofer - Email spoofing test tool.

Sends emails directly to destination MX servers,
bypassing any relay SMTP, to test SPF/DKIM/DMARC configurations.
"""

from src.core import (
    get_dmarc_record,
    get_dns_info,
    get_mx_records,
    get_public_ip,
    get_spf_record,
    send_direct,
)
from src.models import DNSInfo, EmailConfig, SendResult
from src.utils import VERSION as __version__
from src.utils import ErrorType, OutputFormat

__author__ = "SmookeyDev"
__all__ = [
    "__version__",
    "__author__",
    "DNSInfo",
    "EmailConfig",
    "ErrorType",
    "OutputFormat",
    "SendResult",
    "get_dmarc_record",
    "get_dns_info",
    "get_mx_records",
    "get_public_ip",
    "get_spf_record",
    "send_direct",
]
