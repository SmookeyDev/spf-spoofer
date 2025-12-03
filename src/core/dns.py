"""DNS utilities for resolving MX, SPF, and DMARC records."""

import dns.resolver

from src.models.result import DNSInfo
from src.utils.constants import DNS_TIMEOUT


def get_mx_records(domain: str, timeout: int = DNS_TIMEOUT) -> list[tuple[int, str]]:
    """
    Get MX servers for a domain sorted by priority.

    Args:
        domain: The domain to query MX records for.
        timeout: DNS query timeout in seconds.

    Returns:
        List of tuples (priority, server) sorted by priority.
    """
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout

        answers = resolver.resolve(domain, "MX")
        mx_servers = []
        for rdata in answers:
            mx_servers.append((rdata.preference, str(rdata.exchange).rstrip(".")))
        return sorted(mx_servers, key=lambda x: x[0])
    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
        dns.resolver.NoNameservers,
        dns.resolver.Timeout,
    ):
        return []
    except Exception:
        return []


def get_spf_record(domain: str, timeout: int = DNS_TIMEOUT) -> str | None:
    """
    Get SPF record for a domain.

    Args:
        domain: The domain to query SPF record for.
        timeout: DNS query timeout in seconds.

    Returns:
        The SPF record if found, None otherwise.
    """
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout

        answers = resolver.resolve(domain, "TXT")
        for rdata in answers:
            txt = "".join([s.decode() if isinstance(s, bytes) else s for s in rdata.strings])
            if txt.startswith("v=spf1"):
                return txt
    except Exception:
        pass
    return None


def get_dmarc_record(domain: str, timeout: int = DNS_TIMEOUT) -> str | None:
    """
    Get DMARC record for a domain.

    Args:
        domain: The domain to query DMARC record for.
        timeout: DNS query timeout in seconds.

    Returns:
        The DMARC record if found, None otherwise.
    """
    try:
        resolver = dns.resolver.Resolver()
        resolver.timeout = timeout
        resolver.lifetime = timeout

        dmarc_domain = f"_dmarc.{domain}"
        answers = resolver.resolve(dmarc_domain, "TXT")
        for rdata in answers:
            txt = "".join([s.decode() if isinstance(s, bytes) else s for s in rdata.strings])
            if txt.startswith("v=DMARC1"):
                return txt
    except Exception:
        pass
    return None


def get_dns_info(domain: str, timeout: int = DNS_TIMEOUT) -> DNSInfo:
    """
    Get all relevant DNS information for a domain.

    Args:
        domain: The domain to query.
        timeout: DNS query timeout in seconds.

    Returns:
        DNSInfo with all collected information.
    """
    return DNSInfo(
        domain=domain,
        mx_records=get_mx_records(domain, timeout),
        spf_record=get_spf_record(domain, timeout),
        dmarc_record=get_dmarc_record(domain, timeout),
    )

