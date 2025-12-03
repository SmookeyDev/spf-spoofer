"""Direct email sending module for SPF testing."""

import random
import smtplib
import socket
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid

import dkim

from src.core.dns import get_dmarc_record, get_mx_records, get_spf_record
from src.models.config import EmailConfig
from src.models.result import SendResult
from src.utils.constants import (
    DEFAULT_TIMEOUT,
    PRIORITY_VALUES,
    REALISTIC_MAILERS,
    ErrorType,
    Priority,
)


def get_public_ip() -> str:
    """
    Get the public/local IP address of the machine.

    Returns:
        String with the machine's IP address.
    """
    # Try to get IP used for external connections
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        pass

    # Fallback to hostname
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception:
        return "unknown"


def build_message(config: EmailConfig) -> MIMEMultipart:
    """
    Build a realistic email message with proper headers.

    Args:
        config: Email configuration.

    Returns:
        MIMEMultipart object with the built message.
    """
    msg = MIMEMultipart("alternative")

    # === Essential Headers ===
    if config.from_name:
        msg["From"] = formataddr((config.from_name, config.from_email))
    else:
        msg["From"] = config.from_email

    if config.to_name:
        msg["To"] = formataddr((config.to_name, config.to_email))
    else:
        msg["To"] = config.to_email

    msg["Subject"] = config.subject

    # === Date & Message-ID (realistic format) ===
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=config.from_domain)

    # === MIME Version (required for proper emails) ===
    msg["MIME-Version"] = "1.0"

    # === Reply-To ===
    if config.reply_to:
        msg["Reply-To"] = config.reply_to

    # === Organization ===
    if config.organization:
        msg["Organization"] = config.organization

    # === X-Mailer (realistic or custom) ===
    if config.mailer:
        msg["X-Mailer"] = config.mailer
    else:
        msg["X-Mailer"] = random.choice(REALISTIC_MAILERS)

    # === Priority Headers ===
    if config.priority != Priority.NORMAL:
        priority_headers = PRIORITY_VALUES.get(config.priority, {})
        for header, value in priority_headers.items():
            msg[header] = value

    # === List-Unsubscribe (important for avoiding spam) ===
    if config.list_unsubscribe:
        msg["List-Unsubscribe"] = f"<{config.list_unsubscribe}>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

    # === Custom Headers ===
    for header, value in config.custom_headers.items():
        msg[header] = value

    # === Body Content ===
    if config.html:
        # For HTML emails, include both plain text and HTML versions
        plain_text = "This email requires HTML support to view properly."
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(config.body, "html", "utf-8"))
    else:
        msg.attach(MIMEText(config.body, "plain", "utf-8"))

    return msg


def sign_with_dkim(message: str, config: EmailConfig) -> str:
    """
    Sign an email message with DKIM.

    Args:
        message: The email message as string.
        config: Email configuration with DKIM settings.

    Returns:
        The signed email message as string.
    """
    if not config.dkim_key or not config.dkim_selector:
        return message

    # Read private key
    private_key = config.dkim_key.read_bytes()

    # Domain for DKIM (defaults to from_domain)
    domain = config.dkim_domain or config.from_domain

    # Sign the message
    signature = dkim.sign(
        message=message.encode("utf-8"),
        selector=config.dkim_selector.encode("utf-8"),
        domain=domain.encode("utf-8"),
        privkey=private_key,
        include_headers=[
            b"From",
            b"To",
            b"Subject",
            b"Date",
            b"Message-ID",
            b"MIME-Version",
            b"Content-Type",
        ],
    )

    # Prepend DKIM signature to message
    return signature.decode("utf-8") + message


def classify_smtp_error(code: int, message: str) -> ErrorType:
    """
    Classify SMTP error based on code and message.

    Args:
        code: SMTP error code.
        message: Error message.

    Returns:
        Corresponding ErrorType.
    """
    message_lower = message.lower()

    # PTR/reverse DNS errors
    if "ptr" in message_lower or (code == 550 and "5.7.25" in message):
        return ErrorType.NO_PTR_RECORD

    # SPF errors
    if "spf" in message_lower or "5.7.1" in message:
        return ErrorType.SPF_FAIL

    # DKIM errors
    if "dkim" in message_lower:
        return ErrorType.DKIM_FAIL

    # DMARC errors
    if "dmarc" in message_lower:
        return ErrorType.DMARC_FAIL

    # Spam
    if "spam" in message_lower or "5.7.0" in message:
        return ErrorType.SPAM_DETECTED

    # Authentication required
    if "auth" in message_lower and "required" in message_lower:
        return ErrorType.AUTH_REQUIRED

    # Generic rejection
    if code >= 500:
        return ErrorType.REJECTED

    return ErrorType.UNKNOWN


def send_direct(
    config: EmailConfig,
    timeout: int = DEFAULT_TIMEOUT,
    verbose: bool = False,
) -> SendResult:
    """
    Send email directly to the recipient's MX server.

    Args:
        config: Email configuration.
        timeout: SMTP connection timeout in seconds.
        verbose: If True, show SMTP debug output.

    Returns:
        SendResult with the sending result.
    """
    start_time = time.time()
    sender_ip = get_public_ip()
    spf_record = get_spf_record(config.from_domain)
    dmarc_record = get_dmarc_record(config.from_domain)
    mx_records = get_mx_records(config.to_domain)

    # Check for MX servers
    if not mx_records:
        return SendResult(
            success=False,
            error_type=ErrorType.NO_MX_RECORDS,
            sender_ip=sender_ip,
            spf_record=spf_record,
            dmarc_record=dmarc_record,
            error_message=f"No MX servers found for {config.to_domain}",
            duration_ms=(time.time() - start_time) * 1000,
        )

    msg = build_message(config)
    
    # Convert to string and sign with DKIM if configured
    msg_string = msg.as_string()
    if config.dkim_key:
        msg_string = sign_with_dkim(msg_string, config)
    
    last_error: str | None = None
    last_error_type = ErrorType.ALL_MX_FAILED

    # Try each MX server by priority order
    for _, mx_server in mx_records:
        try:
            server = smtplib.SMTP(mx_server, 25, timeout=timeout)

            if verbose:
                server.set_debuglevel(2)

            # EHLO
            hostname = socket.getfqdn()
            server.ehlo(hostname)

            # Try STARTTLS
            try:
                server.starttls()
                server.ehlo(hostname)
            except smtplib.SMTPException:
                pass  # TLS is optional

            # Send
            server.sendmail(config.from_email, [config.to_email], msg_string)
            server.quit()

            return SendResult(
                success=True,
                error_type=ErrorType.SUCCESS,
                sender_ip=sender_ip,
                mx_server=mx_server,
                spf_record=spf_record,
                dmarc_record=dmarc_record,
                duration_ms=(time.time() - start_time) * 1000,
            )

        except smtplib.SMTPRecipientsRefused as e:
            recipient_errors = list(e.recipients.values())
            if recipient_errors:
                code, msg_bytes = recipient_errors[0]
                error_msg = msg_bytes.decode() if isinstance(msg_bytes, bytes) else str(msg_bytes)
                return SendResult(
                    success=False,
                    error_type=ErrorType.RECIPIENT_REFUSED,
                    sender_ip=sender_ip,
                    mx_server=mx_server,
                    spf_record=spf_record,
                    dmarc_record=dmarc_record,
                    error_message=error_msg,
                    smtp_code=code,
                    smtp_message=error_msg,
                    duration_ms=(time.time() - start_time) * 1000,
                )

        except smtplib.SMTPSenderRefused as e:
            error_msg = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
            return SendResult(
                success=False,
                error_type=classify_smtp_error(e.smtp_code, error_msg),
                sender_ip=sender_ip,
                mx_server=mx_server,
                spf_record=spf_record,
                dmarc_record=dmarc_record,
                error_message=error_msg,
                smtp_code=e.smtp_code,
                smtp_message=error_msg,
                duration_ms=(time.time() - start_time) * 1000,
            )

        except smtplib.SMTPDataError as e:
            error_msg = e.smtp_error.decode() if isinstance(e.smtp_error, bytes) else str(e.smtp_error)
            return SendResult(
                success=False,
                error_type=classify_smtp_error(e.smtp_code, error_msg),
                sender_ip=sender_ip,
                mx_server=mx_server,
                spf_record=spf_record,
                dmarc_record=dmarc_record,
                error_message=error_msg,
                smtp_code=e.smtp_code,
                smtp_message=error_msg,
                duration_ms=(time.time() - start_time) * 1000,
            )

        except smtplib.SMTPException as e:
            last_error = str(e)
            last_error_type = ErrorType.REJECTED
            continue

        except socket.timeout:
            last_error = f"Timeout connecting to {mx_server}"
            last_error_type = ErrorType.TIMEOUT
            continue

        except OSError as e:
            last_error = f"Connection error with {mx_server}: {e}"
            last_error_type = ErrorType.CONNECTION_FAILED
            continue

        except Exception as e:
            last_error = str(e)
            last_error_type = ErrorType.UNKNOWN
            continue

    # All MX servers failed
    return SendResult(
        success=False,
        error_type=last_error_type,
        sender_ip=sender_ip,
        spf_record=spf_record,
        dmarc_record=dmarc_record,
        error_message=last_error or "Failed to connect to all MX servers",
        duration_ms=(time.time() - start_time) * 1000,
    )

