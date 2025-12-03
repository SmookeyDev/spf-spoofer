"""Tests for constants and enums."""

from src.utils.constants import (
    DEFAULT_TIMEOUT,
    DNS_TIMEOUT,
    SMTP_PORT,
    VERSION,
    ErrorType,
    OutputFormat,
)


class TestErrorType:
    """Tests for ErrorType enum."""

    def test_all_error_types_exist(self) -> None:
        assert ErrorType.SUCCESS.value == "SUCCESS"
        assert ErrorType.DNS_ERROR.value == "DNS_ERROR"
        assert ErrorType.NO_MX_RECORDS.value == "NO_MX_RECORDS"
        assert ErrorType.SPF_FAIL.value == "SPF_FAIL"
        assert ErrorType.DKIM_FAIL.value == "DKIM_FAIL"
        assert ErrorType.DMARC_FAIL.value == "DMARC_FAIL"
        assert ErrorType.NO_PTR_RECORD.value == "NO_PTR_RECORD"
        assert ErrorType.SPAM_DETECTED.value == "SPAM_DETECTED"

    def test_error_type_is_string(self) -> None:
        assert isinstance(ErrorType.SUCCESS.value, str)
        assert str(ErrorType.SUCCESS) == "ErrorType.SUCCESS"


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_all_formats_exist(self) -> None:
        assert OutputFormat.TEXT.value == "text"
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.QUIET.value == "quiet"


class TestConstants:
    """Tests for constant values."""

    def test_smtp_port(self) -> None:
        assert SMTP_PORT == 25

    def test_default_timeout(self) -> None:
        assert DEFAULT_TIMEOUT == 30

    def test_dns_timeout(self) -> None:
        assert DNS_TIMEOUT == 10

    def test_version_format(self) -> None:
        assert VERSION == "1.0.0"
        parts = VERSION.split(".")
        assert len(parts) == 3

