"""Tests for data models."""

import pytest

from src.models.config import EmailConfig, validate_email
from src.models.result import DNSInfo, SendResult
from src.utils.constants import ErrorType
from src.utils.exceptions import ValidationError


class TestValidateEmail:
    """Tests for email validation."""

    def test_valid_email(self) -> None:
        assert validate_email("user@example.com") is True
        assert validate_email("user.name@example.com") is True
        assert validate_email("user+tag@example.com") is True
        assert validate_email("user@sub.example.com") is True

    def test_invalid_email(self) -> None:
        assert validate_email("") is False
        assert validate_email("invalid") is False
        assert validate_email("@example.com") is False
        assert validate_email("user@") is False
        assert validate_email("user@.com") is False
        assert validate_email("user@example") is False


class TestEmailConfig:
    """Tests for EmailConfig model."""

    def test_valid_config(self) -> None:
        config = EmailConfig(
            from_email="sender@example.com",
            to_email="recipient@example.com",
            subject="Test",
            body="Hello",
        )
        assert config.from_email == "sender@example.com"
        assert config.to_email == "recipient@example.com"
        assert config.subject == "Test"
        assert config.body == "Hello"
        assert config.from_name == ""
        assert config.to_name == ""
        assert config.html is False

    def test_config_with_names(self) -> None:
        config = EmailConfig(
            from_email="sender@example.com",
            to_email="recipient@example.com",
            subject="Test",
            body="Hello",
            from_name="Sender Name",
            to_name="Recipient Name",
        )
        assert config.from_name == "Sender Name"
        assert config.to_name == "Recipient Name"

    def test_config_html_mode(self) -> None:
        config = EmailConfig(
            from_email="sender@example.com",
            to_email="recipient@example.com",
            subject="Test",
            body="<h1>Hello</h1>",
            html=True,
        )
        assert config.html is True

    def test_from_domain(self) -> None:
        config = EmailConfig(
            from_email="user@sender.com",
            to_email="user@recipient.com",
            subject="Test",
            body="Hello",
        )
        assert config.from_domain == "sender.com"

    def test_to_domain(self) -> None:
        config = EmailConfig(
            from_email="user@sender.com",
            to_email="user@recipient.com",
            subject="Test",
            body="Hello",
        )
        assert config.to_domain == "recipient.com"

    def test_missing_from_email(self) -> None:
        with pytest.raises(ValidationError, match="Sender email is required"):
            EmailConfig(
                from_email="",
                to_email="recipient@example.com",
                subject="Test",
                body="Hello",
            )

    def test_missing_to_email(self) -> None:
        with pytest.raises(ValidationError, match="Recipient email is required"):
            EmailConfig(
                from_email="sender@example.com",
                to_email="",
                subject="Test",
                body="Hello",
            )

    def test_missing_subject(self) -> None:
        with pytest.raises(ValidationError, match="Subject is required"):
            EmailConfig(
                from_email="sender@example.com",
                to_email="recipient@example.com",
                subject="",
                body="Hello",
            )

    def test_missing_body(self) -> None:
        with pytest.raises(ValidationError, match="Body is required"):
            EmailConfig(
                from_email="sender@example.com",
                to_email="recipient@example.com",
                subject="Test",
                body="",
            )

    def test_invalid_from_email(self) -> None:
        with pytest.raises(ValidationError, match="Invalid sender email"):
            EmailConfig(
                from_email="invalid",
                to_email="recipient@example.com",
                subject="Test",
                body="Hello",
            )

    def test_invalid_to_email(self) -> None:
        with pytest.raises(ValidationError, match="Invalid recipient email"):
            EmailConfig(
                from_email="sender@example.com",
                to_email="invalid",
                subject="Test",
                body="Hello",
            )


class TestDNSInfo:
    """Tests for DNSInfo model."""

    def test_default_values(self) -> None:
        info = DNSInfo(domain="example.com")
        assert info.domain == "example.com"
        assert info.mx_records == []
        assert info.spf_record is None
        assert info.dmarc_record is None

    def test_with_records(self) -> None:
        info = DNSInfo(
            domain="example.com",
            mx_records=[(10, "mx1.example.com"), (20, "mx2.example.com")],
            spf_record="v=spf1 -all",
            dmarc_record="v=DMARC1; p=reject",
        )
        assert len(info.mx_records) == 2
        assert info.spf_record == "v=spf1 -all"
        assert info.dmarc_record == "v=DMARC1; p=reject"


class TestSendResult:
    """Tests for SendResult model."""

    def test_success_result(self) -> None:
        result = SendResult(
            success=True,
            error_type=ErrorType.SUCCESS,
            sender_ip="192.168.1.1",
            mx_server="mx.example.com",
        )
        assert result.success is True
        assert result.error_type == ErrorType.SUCCESS
        assert result.sender_ip == "192.168.1.1"
        assert result.mx_server == "mx.example.com"

    def test_failure_result(self) -> None:
        result = SendResult(
            success=False,
            error_type=ErrorType.SPF_FAIL,
            sender_ip="192.168.1.1",
            error_message="SPF validation failed",
            smtp_code=550,
        )
        assert result.success is False
        assert result.error_type == ErrorType.SPF_FAIL
        assert result.error_message == "SPF validation failed"
        assert result.smtp_code == 550

    def test_to_dict(self) -> None:
        result = SendResult(
            success=True,
            error_type=ErrorType.SUCCESS,
            sender_ip="192.168.1.1",
            mx_server="mx.example.com",
        )
        data = result.to_dict()
        assert data["success"] is True
        assert data["error_type"] == "SUCCESS"
        assert data["sender_ip"] == "192.168.1.1"
        assert data["mx_server"] == "mx.example.com"
        assert "timestamp" in data

