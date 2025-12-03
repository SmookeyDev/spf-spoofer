"""CLI module for SPF Tester."""

from src.cli.main import main
from src.cli.output import Console, print_dns_info, print_email_details, print_result

__all__ = [
    "Console",
    "main",
    "print_dns_info",
    "print_email_details",
    "print_result",
]

