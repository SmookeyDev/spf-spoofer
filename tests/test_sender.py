"""Tests for email sender."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.sender import build_message, classify_smtp_error, get_public_ip
from src.models.config import EmailConfig
from src.utils.constants import ErrorType


class TestGetPublicIp:
    """Tests for public IP detection."""

    @patch("src.core.sender.socket.socket")
    def test_returns_ip_from_socket(self, mock_socket_class: MagicMock) -> None:
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.getsockname.return_value = ("192.168.1.100", 12345)

        result = get_public_ip()
        assert result == "192.168.1.100"

    @patch("src.core.sender.socket.socket")
    @patch("src.core.sender.socket.gethostbyname")
    def test_fallback_to_hostname(
        self, mock_gethostbyname: MagicMock, mock_socket_class: MagicMock
    ) -> None:
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = Exception("Network error")
        mock_gethostbyname.return_value = "127.0.0.1"

        result = get_public_ip()
        assert result == "127.0.0.1"


class TestBuildMessage:
    """Tests for email message building."""

    def test_builds_plain_text_message(self) -> None:
        config = EmailConfig(
            from_email="sender@example.com",
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test Body",
        )

        msg = build_message(config)

        assert msg["From"] == "sender@example.com"
        assert msg["To"] == "recipient@example.com"
        assert msg["Subject"] == "Test Subject"
        assert "SPFSpoofer" in msg["X-Mailer"]

    def test_builds_message_with_names(self) -> None:
        config = EmailConfig(
            from_email="sender@example.com",
            to_email="recipient@example.com",
            subject="Test",
            body="Hello",
            from_name="Sender Name",
            to_name="Recipient Name",
        )

        msg = build_message(config)

        assert "Sender Name" in msg["From"]
        assert "Recipient Name" in msg["To"]

    def test_builds_html_message(self) -> None:
        config = EmailConfig(
            from_email="sender@example.com",
            to_email="recipient@example.com",
            subject="Test",
            body="<h1>Hello</h1>",
            html=True,
        )

        msg = build_message(config)
        payload = msg.get_payload()[0]

        assert payload.get_content_type() == "text/html"


class TestClassifySmtpError:
    """Tests for SMTP error classification."""

    def test_classifies_ptr_error(self) -> None:
        result = classify_smtp_error(550, "PTR record not found")
        assert result == ErrorType.NO_PTR_RECORD

    def test_classifies_ptr_error_by_code(self) -> None:
        result = classify_smtp_error(550, "5.7.25 IP does not have PTR")
        assert result == ErrorType.NO_PTR_RECORD

    def test_classifies_spf_error(self) -> None:
        result = classify_smtp_error(550, "SPF check failed")
        assert result == ErrorType.SPF_FAIL

    def test_classifies_spf_error_by_code(self) -> None:
        result = classify_smtp_error(550, "5.7.1 Sender not authorized")
        assert result == ErrorType.SPF_FAIL

    def test_classifies_dkim_error(self) -> None:
        result = classify_smtp_error(550, "DKIM signature invalid")
        assert result == ErrorType.DKIM_FAIL

    def test_classifies_dmarc_error(self) -> None:
        result = classify_smtp_error(550, "DMARC policy violation")
        assert result == ErrorType.DMARC_FAIL

    def test_classifies_spam_error(self) -> None:
        result = classify_smtp_error(550, "Message classified as spam")
        assert result == ErrorType.SPAM_DETECTED

    def test_classifies_spam_by_code(self) -> None:
        result = classify_smtp_error(550, "5.7.0 Message rejected")
        assert result == ErrorType.SPAM_DETECTED

    def test_classifies_auth_required(self) -> None:
        result = classify_smtp_error(530, "Authentication required")
        assert result == ErrorType.AUTH_REQUIRED

    def test_classifies_generic_rejection(self) -> None:
        result = classify_smtp_error(550, "Unknown error")
        assert result == ErrorType.REJECTED

    def test_classifies_unknown_error(self) -> None:
        result = classify_smtp_error(400, "Temporary failure")
        assert result == ErrorType.UNKNOWN

