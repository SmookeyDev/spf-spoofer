# SPF Spoofer

🔓 Test email authentication by sending spoofed emails directly to MX servers.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.14+-brightgreen.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)]()

## 📝 Table of Contents

- [🧐 About](#-about)
- [⚡ Features](#-features)
- [💻 Installation](#-installation)
- [🚀 Usage](#-usage)
- [📁 Project Structure](#-project-structure)
- [🔧 Technical Details](#-technical-details)
- [🔒 Security Considerations](#-security-considerations)
- [🎯 Use Cases](#-use-cases)
- [💬 Support](#-support)

## 🧐 About

**SPF Spoofer** is a security testing tool developed by **SmookeyDev** that sends emails directly to destination MX servers, bypassing any relay SMTP. This simulates how an attacker would attempt to spoof emails from your domain, allowing you to verify that your SPF/DKIM/DMARC configurations are properly blocking unauthorized senders.

## ⚡ Features

- 📡 **Direct MX Sending** - Sends emails directly to recipient's MX server on port 25
- 🔍 **DNS Lookup** - Automatically fetches SPF, DMARC, and MX records
- 🏷️ **Error Classification** - Identifies rejection reasons (SPF, PTR, DMARC, Spam)
- 🌐 **HTML Support** - Send emails with HTML body content
- 📄 **File Input** - Read email body from external files
- 🔐 **DKIM Signing** - Sign emails with custom DKIM keys
- 🎭 **Realistic Headers** - Anti-spam headers (Reply-To, Organization, List-Unsubscribe)
- 📊 **Multiple Outputs** - Text, JSON, and quiet output modes
- 🐛 **Verbose Mode** - Debug SMTP communication in real-time

## 💻 Installation

### Quick Start

```bash
# Clone the repository
git clone https://github.com/SmookeyDev/spfspoofer.git
cd spfspoofer

# Install with uv (recommended)
uv sync

# Run
uv run spfspoofer --help
```

### Alternative Installation

```bash
# Using pip
pip install -e .
spfspoofer --help
```

### Requirements

- Python 3.14 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

## 🚀 Usage

### Basic Example

```bash
spfspoofer \
  --from sender@target-domain.com \
  --to recipient@example.com \
  --subject "Security Test" \
  --body "This is a spoofing test."
```

### Command Reference

#### Required Arguments

| Argument | Description |
|----------|-------------|
| `--from EMAIL` | Sender email address (domain to test) |
| `--to EMAIL` | Recipient email address |
| `--subject TEXT` | Email subject line |

#### Body Content (one required)

| Argument | Description |
|----------|-------------|
| `--body TEXT` | Email body as inline text |
| `--body-file FILE` | Read email body from file |

#### Email Options

| Argument | Default | Description |
|----------|---------|-------------|
| `--from-name NAME` | - | Sender display name |
| `--to-name NAME` | - | Recipient display name |
| `--html` | `false` | Send body as HTML instead of plain text |

#### Realistic Headers (Anti-Spam)

| Argument | Default | Description |
|----------|---------|-------------|
| `--reply-to EMAIL` | - | Reply-To email address |
| `--organization NAME` | - | Organization name header |
| `--priority LEVEL` | `normal` | Email priority: `high`, `normal`, `low` |
| `--mailer STRING` | random | X-Mailer header (default: random realistic client) |
| `--list-unsubscribe URL` | - | List-Unsubscribe URL (helps avoid spam filters) |
| `--header NAME:VALUE` | - | Custom header (can be used multiple times) |

#### DKIM Signing

| Argument | Description |
|----------|-------------|
| `--dkim-key FILE` | Path to DKIM private key file (PEM format) |
| `--dkim-selector SELECTOR` | DKIM selector (e.g., `selector1`, `default`) |
| `--dkim-domain DOMAIN` | DKIM domain (defaults to sender domain) |

#### Output Options

| Argument | Default | Description |
|----------|---------|-------------|
| `--format FORMAT` | `text` | Output format: `text`, `json`, `quiet` |
| `--no-color` | `false` | Disable colored terminal output |
| `-v, --verbose` | `false` | Show SMTP debug communication |

#### Execution Options

| Argument | Default | Description |
|----------|---------|-------------|
| `--dns-only` | `false` | Only show DNS info, don't send email |
| `--timeout SEC` | `30` | SMTP connection timeout in seconds |
| `--version` | - | Show version and exit |
| `-h, --help` | - | Show help message and exit |

### Examples

<details>
<summary><b>Basic spoofing test</b></summary>

```bash
spfspoofer \
  --from ceo@target-company.com \
  --to employee@target-company.com \
  --subject "Urgent: Wire Transfer" \
  --body "Please transfer $50,000 to account XXX"
```

</details>

<details>
<summary><b>Realistic email with anti-spam headers</b></summary>

```bash
spfspoofer \
  --from noreply@company.com \
  --from-name "Company Name" \
  --to user@example.com \
  --subject "Important Update" \
  --body-file email.html \
  --html \
  --reply-to support@company.com \
  --organization "Company Inc." \
  --list-unsubscribe "https://company.com/unsubscribe"
```

</details>

<details>
<summary><b>With DKIM signing</b></summary>

```bash
# Generate a DKIM key pair
openssl genrsa -out dkim_private.pem 2048

# Send with DKIM signature
spfspoofer \
  --from sender@domain.com \
  --to recipient@example.com \
  --subject "DKIM Test" \
  --body "Testing DKIM signature" \
  --dkim-key dkim_private.pem \
  --dkim-selector "selector1"
```

> ⚠️ DKIM will show `permerror` unless you publish the public key in DNS

</details>

<details>
<summary><b>DNS-only mode</b> - Check records without sending</summary>

```bash
spfspoofer \
  --from test@domain.com \
  --to user@example.com \
  --subject "Test" \
  --body "Test" \
  --dns-only
```

</details>

<details>
<summary><b>Full example with all options</b></summary>

```bash
spfspoofer \
  --from "noreply@company.com" \
  --from-name "Company Name" \
  --to "recipient@example.com" \
  --to-name "John Doe" \
  --subject "Security Test Email" \
  --body-file template.html \
  --html \
  --reply-to "support@company.com" \
  --organization "Company Inc." \
  --priority high \
  --list-unsubscribe "https://company.com/unsub" \
  --header "X-Campaign-ID:test123" \
  --dkim-key private.pem \
  --dkim-selector "default" \
  --timeout 60 \
  --verbose
```

</details>

### Understanding Results

| Result | Meaning |
|--------|---------|
| ✅ **Email Sent** | MX server accepted - check inbox/spam and headers |
| ❌ **SPF_FAIL** | IP not authorized in SPF record |
| ❌ **NO_PTR_RECORD** | Missing reverse DNS (PTR) |
| ❌ **DMARC_FAIL** | DMARC policy rejected the email |
| ❌ **SPAM_DETECTED** | Classified as spam by server |
| ❌ **RECIPIENT_REFUSED** | Invalid or blocked recipient |

> 💡 **Tip:** Blocked results often mean security is working correctly!

## 📁 Project Structure

```
spfspoofer/
├── src/
│   ├── __init__.py
│   ├── cli/                   # Command-line interface
│   │   ├── main.py            # Entry point & argument parsing
│   │   └── output.py          # Console formatting
│   ├── core/                  # Core business logic
│   │   ├── dns.py             # DNS resolution (MX, SPF, DMARC)
│   │   └── sender.py          # Direct SMTP sending + DKIM
│   ├── models/                # Data models
│   │   ├── config.py          # EmailConfig
│   │   └── result.py          # SendResult, DNSInfo
│   └── utils/                 # Utilities
│       ├── constants.py       # Enums and constants
│       └── exceptions.py      # Custom exceptions
├── tests/                     # Test suite
├── pyproject.toml
├── LICENSE
└── README.md
```

## 🔧 Technical Details

### How It Works

```
1. DNS Resolution     →  Fetch MX, SPF, DMARC records
2. Build Message      →  Construct email with realistic headers
3. DKIM Signing       →  Sign message if key provided
4. SMTP Connection    →  Connect to MX server on port 25
5. TLS Upgrade        →  STARTTLS if available
6. Send Email         →  Deliver without authentication
7. Analyze Response   →  Classify success/rejection
```

### SMTP Flow

```
Client                          MX Server
  │                                 │
  │──────── TCP Connect :25 ───────►│
  │◄──────── 220 Welcome ───────────│
  │──────── EHLO hostname ─────────►│
  │◄──────── 250 Extensions ────────│
  │──────── STARTTLS ──────────────►│
  │◄──────── 220 Ready ─────────────│
  │════════ TLS Handshake ══════════│
  │──────── MAIL FROM ─────────────►│
  │◄──────── 250 OK ────────────────│
  │──────── RCPT TO ───────────────►│
  │◄──────── 250 OK ────────────────│
  │──────── DATA ──────────────────►│
  │──────── [Message + DKIM] ──────►│
  │◄──────── 250 OK / 550 Reject ───│
  │──────── QUIT ──────────────────►│
```

### Email Headers Added

| Header | Purpose |
|--------|---------|
| `From`, `To`, `Subject` | Standard email headers |
| `Date`, `Message-ID` | Timestamp and unique identifier |
| `MIME-Version` | Required for proper email formatting |
| `Reply-To` | Legitimate reply address |
| `Organization` | Sender organization name |
| `X-Mailer` | Email client identifier (randomized) |
| `X-Priority`, `Importance` | Email priority flags |
| `List-Unsubscribe` | One-click unsubscribe (anti-spam) |
| `DKIM-Signature` | Cryptographic signature (if key provided) |

### Error Codes

| Error Type | SMTP Code | Cause |
|------------|-----------|-------|
| `SUCCESS` | 250 | Email accepted |
| `SPF_FAIL` | 550 / 5.7.1 | SPF validation failed |
| `NO_PTR_RECORD` | 550 / 5.7.25 | Missing reverse DNS |
| `DMARC_FAIL` | 550 / 5.7.26 | DMARC policy rejection |
| `SPAM_DETECTED` | 550 / 5.7.0 | Spam classification |
| `AUTH_REQUIRED` | 530 | Authentication required |
| `TIMEOUT` | - | Connection timeout |

## 🔒 Security Considerations

- ⚠️ **Authorized Testing Only**: Only test domains you own or have permission to test
- 🛡️ **Legal Compliance**: Email spoofing may be illegal without authorization
- 🔐 **Responsible Disclosure**: Report vulnerabilities through proper channels
- 📊 **Logging**: Your IP will be logged by receiving mail servers
- 🚫 **Not for Malicious Use**: This tool is for security testing only

## 🎯 Use Cases

- ✅ **SPF Validation** - Verify SPF records block unauthorized senders
- ✅ **DMARC Testing** - Test DMARC policies before enforcement
- ✅ **DKIM Verification** - Test DKIM signature validation
- ✅ **Security Audits** - Assess email authentication posture
- ✅ **Penetration Testing** - Authorized email security assessments
- ✅ **Configuration Verification** - Confirm DNS records are working
- ⚠️ **Phishing Simulation** - Only with proper authorization

## 💬 Support

For more information and support:

- 🐛 **Issues**: [Create an issue on GitHub](https://github.com/SmookeyDev/spfspoofer/issues)
- 💡 **Feature Requests**: Submit via GitHub issues
- 📚 **SPF Documentation**: [RFC 7208](https://tools.ietf.org/html/rfc7208)
- 📚 **DKIM Documentation**: [RFC 6376](https://tools.ietf.org/html/rfc6376)
- 📚 **DMARC Documentation**: [RFC 7489](https://tools.ietf.org/html/rfc7489)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Developed with ❤️ by SmookeyDev</sub>
</div>