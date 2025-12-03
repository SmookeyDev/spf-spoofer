"""Command-line interface for SPF Spoofer."""

import argparse
import sys
from pathlib import Path

from src.cli.output import Console, print_dns_info, print_email_details, print_result
from src.core.sender import send_direct
from src.models.config import EmailConfig
from src.utils.constants import VERSION, OutputFormat
from src.utils.exceptions import ValidationError


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="spfspoofer",
        description="A robust SPF/DKIM/DMARC testing tool that sends emails directly to MX servers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --from sender@domain.com --to recipient@domain.com --subject "Test" --body "Hello"
  %(prog)s --from sender@domain.com --to recipient@domain.com --subject "Test" --body-file email.html --html
  %(prog)s --from sender@domain.com --to recipient@domain.com --dns-only
  %(prog)s --from sender@domain.com --to recipient@domain.com --format json

Notes:
  - Emails are sent directly to the recipient's MX server on port 25
  - No SMTP authentication is used (simulates external server sending)
  - Use this to test if SPF/DKIM/DMARC configurations are working correctly
        """,
    )

    # Required email fields
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "--from",
        dest="from_email",
        required=True,
        metavar="EMAIL",
        help="Sender email address",
    )
    required.add_argument(
        "--to",
        dest="to_email",
        required=True,
        metavar="EMAIL",
        help="Recipient email address",
    )
    required.add_argument(
        "--subject",
        required=True,
        metavar="TEXT",
        help="Email subject",
    )
    required.add_argument(
        "--body",
        metavar="TEXT",
        help="Email body content",
    )

    # Optional fields
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument(
        "--body-file",
        dest="body_file",
        metavar="FILE",
        help="Read email body from file",
    )
    optional.add_argument(
        "--html",
        action="store_true",
        help="Send body as HTML instead of plain text",
    )
    optional.add_argument(
        "--from-name",
        dest="from_name",
        default="",
        metavar="NAME",
        help="Sender display name",
    )
    optional.add_argument(
        "--to-name",
        dest="to_name",
        default="",
        metavar="NAME",
        help="Recipient display name",
    )

    # Execution options
    options = parser.add_argument_group("options")
    options.add_argument(
        "--dns-only",
        dest="dns_only",
        action="store_true",
        help="Only show DNS information without sending email",
    )
    options.add_argument(
        "--timeout",
        type=int,
        default=30,
        metavar="SEC",
        help="SMTP connection timeout in seconds (default: 30)",
    )
    options.add_argument(
        "--format",
        dest="output_format",
        choices=["text", "json", "quiet"],
        default="text",
        help="Output format: text (default), json, quiet",
    )
    options.add_argument(
        "--no-color",
        dest="no_color",
        action="store_true",
        help="Disable colored output",
    )
    options.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose mode (show SMTP debug)",
    )
    options.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )

    return parser.parse_args()


def main() -> None:
    """Main CLI function."""
    args = parse_args()

    # Configure console
    output_format = OutputFormat(args.output_format)
    console = Console(format=output_format, color=not args.no_color)

    # Get body content
    body = args.body
    if args.body_file:
        try:
            body = Path(args.body_file).read_text(encoding="utf-8")
        except FileNotFoundError:
            console.error(f"File not found: {args.body_file}")
            sys.exit(1)
        except PermissionError:
            console.error(f"Permission denied: {args.body_file}")
            sys.exit(1)

    if not body:
        console.error("Either --body or --body-file is required")
        sys.exit(1)

    # Validate and create configuration
    try:
        config = EmailConfig(
            from_email=args.from_email,
            from_name=args.from_name,
            to_email=args.to_email,
            to_name=args.to_name,
            subject=args.subject,
            body=body,
            html=args.html,
        )
    except ValidationError as e:
        console.error(str(e))
        sys.exit(1)

    # Header
    console.header("🔓 SPF SPOOFER - Email Spoofing Test Tool")

    # Show DNS information
    print_dns_info(console, config.from_domain, config.to_domain)

    # DNS-only mode
    if args.dns_only:
        if output_format == OutputFormat.TEXT:
            print()
            console.info("Mode", "DNS-only (email not sent)", indent=0)
        sys.exit(0)

    # Show email details
    print_email_details(console, config)

    # Send
    if output_format == OutputFormat.TEXT:
        console.section("📤 Sending...")

    result = send_direct(config, timeout=args.timeout, verbose=args.verbose)

    # Result
    print_result(console, result, config)

    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()

