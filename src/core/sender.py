"""Direct email sending module for SPF testing."""

import smtplib
import socket
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate

from src.core.dns import get_dmarc_record, get_mx_records, get_spf_record
from src.models.config import EmailConfig
from src.models.result import SendResult
from src.utils.constants import DEFAULT_TIMEOUT, USER_AGENT, ErrorType


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
    Build the email message.

    Args:
        config: Email configuration.

    Returns:
        MIMEMultipart object with the built message.
    """
    msg = MIMEMultipart("alternative")

    # Main headers
    if config.from_name:
        msg["From"] = formataddr((config.from_name, config.from_email))
    else:
        msg["From"] = config.from_email

    if config.to_name:
        msg["To"] = formataddr((config.to_name, config.to_email))
    else:
        msg["To"] = config.to_email

    msg["Subject"] = config.subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = (
        f"<{datetime.now().strftime('%Y%m%d%H%M%S.%f')}.spf-test@{config.from_domain}>"
    )
    msg["X-Mailer"] = USER_AGENT

    # Body
    content_type = "html" if config.html else "plain"
    body_part = MIMEText(config.body, content_type, "utf-8")
    msg.attach(body_part)

    return msg


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
        TestResult with the sending result.
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
            server.sendmail(config.from_email, [config.to_email], msg.as_string())
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
    return TestResult(
        success=False,
        error_type=last_error_type,
        sender_ip=sender_ip,
        spf_record=spf_record,
        dmarc_record=dmarc_record,
        error_message=last_error or "Failed to connect to all MX servers",
        duration_ms=(time.time() - start_time) * 1000,
    )

