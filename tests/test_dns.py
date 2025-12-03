"""Tests for DNS utilities."""

from unittest.mock import MagicMock, patch

import pytest

from src.core.dns import get_dmarc_record, get_dns_info, get_mx_records, get_spf_record


class TestGetMxRecords:
    """Tests for MX record resolution."""

    @patch("src.core.dns.dns.resolver.Resolver")
    def test_returns_sorted_mx_records(self, mock_resolver_class: MagicMock) -> None:
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        # Create mock MX records
        mx1 = MagicMock()
        mx1.preference = 20
        mx1.exchange = "mx2.example.com."

        mx2 = MagicMock()
        mx2.preference = 10
        mx2.exchange = "mx1.example.com."

        mock_resolver.resolve.return_value = [mx1, mx2]

        result = get_mx_records("example.com")

        assert len(result) == 2
        assert result[0] == (10, "mx1.example.com")
        assert result[1] == (20, "mx2.example.com")

    @patch("src.core.dns.dns.resolver.Resolver")
    def test_returns_empty_on_nxdomain(self, mock_resolver_class: MagicMock) -> None:
        import dns.resolver

        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver
        mock_resolver.resolve.side_effect = dns.resolver.NXDOMAIN()

        result = get_mx_records("nonexistent.example.com")
        assert result == []

    @patch("src.core.dns.dns.resolver.Resolver")
    def test_returns_empty_on_timeout(self, mock_resolver_class: MagicMock) -> None:
        import dns.resolver

        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver
        mock_resolver.resolve.side_effect = dns.resolver.Timeout()

        result = get_mx_records("example.com")
        assert result == []


class TestGetSpfRecord:
    """Tests for SPF record resolution."""

    @patch("src.core.dns.dns.resolver.Resolver")
    def test_returns_spf_record(self, mock_resolver_class: MagicMock) -> None:
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        txt1 = MagicMock()
        txt1.strings = [b"v=spf1 include:_spf.google.com -all"]

        mock_resolver.resolve.return_value = [txt1]

        result = get_spf_record("example.com")
        assert result == "v=spf1 include:_spf.google.com -all"

    @patch("src.core.dns.dns.resolver.Resolver")
    def test_ignores_non_spf_txt_records(self, mock_resolver_class: MagicMock) -> None:
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        txt1 = MagicMock()
        txt1.strings = [b"google-site-verification=abc123"]

        txt2 = MagicMock()
        txt2.strings = [b"v=spf1 -all"]

        mock_resolver.resolve.return_value = [txt1, txt2]

        result = get_spf_record("example.com")
        assert result == "v=spf1 -all"

    @patch("src.core.dns.dns.resolver.Resolver")
    def test_returns_none_when_no_spf(self, mock_resolver_class: MagicMock) -> None:
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        txt1 = MagicMock()
        txt1.strings = [b"google-site-verification=abc123"]

        mock_resolver.resolve.return_value = [txt1]

        result = get_spf_record("example.com")
        assert result is None


class TestGetDmarcRecord:
    """Tests for DMARC record resolution."""

    @patch("src.core.dns.dns.resolver.Resolver")
    def test_returns_dmarc_record(self, mock_resolver_class: MagicMock) -> None:
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver

        txt = MagicMock()
        txt.strings = [b"v=DMARC1; p=reject; rua=mailto:dmarc@example.com"]

        mock_resolver.resolve.return_value = [txt]

        result = get_dmarc_record("example.com")
        assert result == "v=DMARC1; p=reject; rua=mailto:dmarc@example.com"

    @patch("src.core.dns.dns.resolver.Resolver")
    def test_queries_dmarc_subdomain(self, mock_resolver_class: MagicMock) -> None:
        mock_resolver = MagicMock()
        mock_resolver_class.return_value = mock_resolver
        mock_resolver.resolve.return_value = []

        get_dmarc_record("example.com")

        mock_resolver.resolve.assert_called_with("_dmarc.example.com", "TXT")


class TestGetDnsInfo:
    """Tests for combined DNS info retrieval."""

    @patch("src.core.dns.get_mx_records")
    @patch("src.core.dns.get_spf_record")
    @patch("src.core.dns.get_dmarc_record")
    def test_combines_all_records(
        self,
        mock_dmarc: MagicMock,
        mock_spf: MagicMock,
        mock_mx: MagicMock,
    ) -> None:
        mock_mx.return_value = [(10, "mx.example.com")]
        mock_spf.return_value = "v=spf1 -all"
        mock_dmarc.return_value = "v=DMARC1; p=reject"

        result = get_dns_info("example.com")

        assert result.domain == "example.com"
        assert result.mx_records == [(10, "mx.example.com")]
        assert result.spf_record == "v=spf1 -all"
        assert result.dmarc_record == "v=DMARC1; p=reject"

