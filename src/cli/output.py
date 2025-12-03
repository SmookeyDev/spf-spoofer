"""Console output formatting."""

import json
import sys
from email.utils import formataddr
from typing import Any

from src.core.dns import get_dns_info
from src.core.sender import get_public_ip
from src.models.config import EmailConfig
from src.models.result import DNSInfo, SendResult
from src.utils.constants import ErrorType, OutputFormat


class Console:
    """Console output manager."""

    def __init__(self, format: OutputFormat = OutputFormat.TEXT, color: bool = True) -> None:
        self.format = format
        self.color = color and sys.stdout.isatty()

    def _c(self, text: str, code: str) -> str:
        """Apply ANSI color if enabled."""
        if not self.color:
            return text
        colors: dict[str, str] = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "bold": "\033[1m",
            "dim": "\033[2m",
            "reset": "\033[0m",
        }
        return f"{colors.get(code, '')}{text}{colors['reset']}"

    def header(self, title: str) -> None:
        """Print header."""
        if self.format != OutputFormat.TEXT:
            return

        width = 70
        print()
        print(self._c("=" * width, "cyan"))
        print(self._c(f"  {title}", "bold"))
        print(self._c("=" * width, "cyan"))

    def section(self, title: str) -> None:
        """Print section title."""
        if self.format != OutputFormat.TEXT:
            return
        print(f"\n{self._c(title, 'bold')}")
        print(self._c("-" * 50, "dim"))

    def info(self, label: str, value: str, indent: int = 0) -> None:
        """Print information."""
        if self.format != OutputFormat.TEXT:
            return
        spaces = "  " * indent
        print(f"{spaces}{self._c(label + ':', 'cyan')} {value}")

    def success(self, message: str) -> None:
        """Print success message."""
        if self.format != OutputFormat.TEXT:
            return
        print(self._c(f"✅ {message}", "green"))

    def error(self, message: str) -> None:
        """Print error message."""
        if self.format != OutputFormat.TEXT:
            return
        print(self._c(f"❌ {message}", "red"))

    def warning(self, message: str) -> None:
        """Print warning message."""
        if self.format != OutputFormat.TEXT:
            return
        print(self._c(f"⚠️  {message}", "yellow"))

    def bullet(self, message: str, indent: int = 1) -> None:
        """Print list item."""
        if self.format != OutputFormat.TEXT:
            return
        spaces = "  " * indent
        print(f"{spaces}• {message}")


def print_dns_info(console: Console, from_domain: str, to_domain: str) -> tuple[DNSInfo, DNSInfo]:
    """
    Print DNS information for domains.

    Returns:
        Tuple with (sender_dns_info, recipient_dns_info).
    """
    console.section("📋 Sender DNS Information")

    from_dns = get_dns_info(from_domain)

    if from_dns.spf_record:
        console.info("SPF", from_dns.spf_record, indent=1)
    else:
        console.warning(f"No SPF record found for {from_domain}")

    if from_dns.dmarc_record:
        console.info("DMARC", from_dns.dmarc_record, indent=1)
    else:
        console.info("DMARC", "Not configured", indent=1)

    sender_ip = get_public_ip()
    console.info("Sender IP", sender_ip, indent=1)
    console.warning("If this IP is not in the SPF record, the email will fail validation!")

    console.section("📡 Recipient MX Servers")

    to_dns = get_dns_info(to_domain)

    if to_dns.mx_records:
        for priority, server in to_dns.mx_records:
            console.bullet(f"[{priority}] {server}")
    else:
        console.error(f"No MX servers found for {to_domain}")

    return from_dns, to_dns


def print_email_details(console: Console, config: EmailConfig) -> None:
    """Print email details to be sent."""
    console.section("📧 Email Details")

    from_addr = (
        formataddr((config.from_name, config.from_email))
        if config.from_name
        else config.from_email
    )
    to_addr = (
        formataddr((config.to_name, config.to_email)) if config.to_name else config.to_email
    )

    console.info("From", from_addr, indent=1)
    console.info("To", to_addr, indent=1)
    console.info("Subject", config.subject, indent=1)


def print_result(console: Console, result: SendResult, config: EmailConfig) -> None:
    """Print test result."""
    if console.format == OutputFormat.JSON:
        output: dict[str, Any] = {
            "config": {
                "from_email": config.from_email,
                "from_name": config.from_name,
                "to_email": config.to_email,
                "to_name": config.to_name,
                "subject": config.subject,
            },
            "result": result.to_dict(),
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    if console.format == OutputFormat.QUIET:
        return

    console.header("📊 TEST RESULT")

    if result.success:
        console.success(f"Email sent successfully via {result.mx_server}!")
        print()
        print("Check the recipient's inbox for:")
        console.bullet("Whether the email arrived in inbox or spam")
        console.bullet("Authentication-Results and Received-SPF headers")
        console.bullet("Any SPF/DKIM/DMARC failure indicators")
    else:
        console.error("Sending blocked")
        print()

        console.info("Error type", result.error_type.value, indent=1)

        if result.smtp_code:
            console.info("SMTP code", str(result.smtp_code), indent=1)

        if result.error_message:
            console.info("Message", result.error_message[:100], indent=1)

        # Explanations by error type
        explanations: dict[ErrorType, str] = {
            ErrorType.NO_PTR_RECORD: "The IP does not have a PTR (reverse DNS) record configured.",
            ErrorType.SPF_FAIL: "The sending IP is not authorized in the domain's SPF record.",
            ErrorType.DKIM_FAIL: "The email's DKIM signature is invalid or missing.",
            ErrorType.DMARC_FAIL: "The domain's DMARC policy rejected the email.",
            ErrorType.SPAM_DETECTED: "The email was classified as spam by the server.",
            ErrorType.SENDER_REFUSED: "The server refused the sender (possible SPF failure).",
            ErrorType.RECIPIENT_REFUSED: "The recipient does not exist or was refused.",
            ErrorType.AUTH_REQUIRED: "The server requires SMTP authentication.",
            ErrorType.NO_MX_RECORDS: "Could not find MX servers for the domain.",
            ErrorType.TIMEOUT: "Timeout while trying to connect to MX servers.",
            ErrorType.CONNECTION_FAILED: "Connection failure with MX servers.",
        }

        if result.error_type in explanations:
            print()
            console.info("Explanation", explanations[result.error_type], indent=1)

        # If blocked by SPF/PTR, this is expected behavior
        if result.error_type in (
            ErrorType.SPF_FAIL,
            ErrorType.NO_PTR_RECORD,
            ErrorType.SENDER_REFUSED,
        ):
            print()
            console.success("This confirms that email protections are working!")
            console.bullet("Emails from unauthorized IPs are correctly rejected.")

    if result.duration_ms:
        print()
        console.info("Duration", f"{result.duration_ms:.0f}ms", indent=1)

    print()

