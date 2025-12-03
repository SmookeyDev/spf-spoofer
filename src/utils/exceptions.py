"""Custom exceptions for SPF Tester."""


class SPFTesterError(Exception):
    """Base exception for SPF Tester."""


class DNSError(SPFTesterError):
    """Error resolving DNS records."""


class ConfigError(SPFTesterError):
    """Configuration error."""


class SMTPError(SPFTesterError):
    """SMTP communication error."""


class ValidationError(SPFTesterError):
    """Data validation error."""

