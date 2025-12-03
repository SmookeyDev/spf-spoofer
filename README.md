# SPF Spoofer

🔓 Test email authentication by sending spoofed emails directly to MX servers.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.14+-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

## 📝 Table of Contents

- [🧐 About](#-about)
- [⚡ Features](#-features)
- [💻 Installation](#-installation)
- [🚀 How to Use](#-how-to-use)
- [📁 Project Structure](#-project-structure)
- [🔧 Technical Details](#-technical-details)
- [🔒 Security Considerations](#-security-considerations)
- [🎯 Use Cases](#-use-cases)
- [💬 Support](#-support)

## 🧐 About

This repository contains an **SPF Spoofer** tool developed by **SmookeyDev**. The tool allows you to test email authentication configurations (SPF/DKIM/DMARC) by sending emails directly to destination MX servers, bypassing any relay SMTP. This simulates how an attacker would attempt to spoof emails from your domain.

**Why use this?**
- Verify that your SPF records are correctly blocking unauthorized senders
- Test DMARC policies before enforcement
- Audit email security configurations
- Validate that spoofed emails are properly rejected

## ⚡ Features

| Feature | Status | Description |
|---------|--------|-------------|
| Direct MX Sending | ✅ | Sends emails directly to recipient's MX server |
| SPF Record Lookup | ✅ | Automatically fetches and displays SPF records |
| DMARC Record Lookup | ✅ | Checks DMARC policy configuration |
| MX Resolution | ✅ | Resolves and prioritizes MX servers |
| Error Classification | ✅ | Identifies specific rejection reasons (SPF, PTR, DMARC) |
| HTML Support | ✅ | Send emails with HTML body |
| File Input | ✅ | Read email body from file |
| Multiple Output Formats | ✅ | Text, JSON, and quiet modes |
| Colored Output | ✅ | Beautiful terminal output with colors |
| Timeout Configuration | ✅ | Configurable SMTP timeouts |
| Verbose Mode | ✅ | Debug SMTP communication |

## 💻 Installation

### Prerequisites

- Python 3.14 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/SmookeyDev/spfspoofer.git
cd spfspoofer

# Install dependencies
uv sync

# Run the tool
uv run spfspoofer --help
```

### Alternative Installation (pip)

```bash
# Clone and install
git clone https://github.com/SmookeyDev/spfspoofer.git
cd spfspoofer
pip install -e .

# Run
spfspoofer --help
```

### Dependencies Overview

The project uses the following Python packages:

- **dnspython>=2.4.0** - DNS resolution for MX, SPF, and DMARC records

All dependencies are automatically installed via `uv sync` or `pip install`.

## 🚀 How to Use

### Basic Usage

```bash
spfspoofer \
  --from sender@target-domain.com \
  --to recipient@example.com \
  --subject "Security Test" \
  --body "This is a spoofing test email."
```

### Command Options

| Option | Required | Description |
|--------|----------|-------------|
| `--from EMAIL` | ✅ | Sender email address (the domain to test) |
| `--to EMAIL` | ✅ | Recipient email address |
| `--subject TEXT` | ✅ | Email subject |
| `--body TEXT` | ❌* | Email body content |
| `--body-file FILE` | ❌* | Read email body from file |
| `--html` | ❌ | Send body as HTML instead of plain text |
| `--from-name NAME` | ❌ | Sender display name |
| `--to-name NAME` | ❌ | Recipient display name |
| `--dns-only` | ❌ | Only show DNS info without sending |
| `--timeout SEC` | ❌ | SMTP timeout in seconds (default: 30) |
| `--format FORMAT` | ❌ | Output format: text, json, quiet |
| `--no-color` | ❌ | Disable colored output |
| `-v, --verbose` | ❌ | Show SMTP debug output |
| `--version` | ❌ | Show version number |

> *Either `--body` or `--body-file` is required.

### Examples

**DNS-only mode (no email sent):**
```bash
spfspoofer \
  --from test@domain.com \
  --to user@example.com \
  --subject "Test" \
  --body "Test" \
  --dns-only
```

**JSON output for automation:**
```bash
spfspoofer \
  --from test@domain.com \
  --to user@example.com \
  --subject "Test" \
  --body "Test" \
  --format json
```

**HTML email from file:**
```bash
spfspoofer \
  --from test@domain.com \
  --to user@example.com \
  --subject "Test" \
  --body-file email.html \
  --html
```

**Verbose mode for debugging:**
```bash
spfspoofer \
  --from test@domain.com \
  --to user@example.com \
  --subject "Test" \
  --body "Test" \
  -v
```

### Understanding Results

**✅ Email Sent Successfully:**
- The MX server accepted the email
- Check recipient's inbox/spam folder
- Examine `Authentication-Results` headers

**❌ Sending Blocked:**
- `SPF_FAIL` - IP not authorized in SPF record ✓
- `NO_PTR_RECORD` - Missing reverse DNS ✓
- `DMARC_FAIL` - DMARC policy rejected email ✓
- `SPAM_DETECTED` - Classified as spam
- `RECIPIENT_REFUSED` - Invalid recipient

> **Note:** Blocked results often indicate that security is working correctly!

## 📁 Project Structure

```
spfspoofer/
├── src/
│   ├── __init__.py            # Package exports
│   │
│   ├── cli/                   # Command-line interface
│   │   ├── __init__.py
│   │   ├── main.py            # CLI entry point
│   │   └── output.py          # Console formatting
│   │
│   ├── core/                  # Core business logic
│   │   ├── __init__.py
│   │   ├── dns.py             # DNS resolution (MX, SPF, DMARC)
│   │   └── sender.py          # Direct SMTP sending
│   │
│   ├── models/                # Data models
│   │   ├── __init__.py
│   │   ├── config.py          # EmailConfig model
│   │   └── result.py          # TestResult, DNSInfo models
│   │
│   └── utils/                 # Utilities
│       ├── __init__.py
│       ├── constants.py       # Constants and enums
│       └── exceptions.py      # Custom exceptions
│
├── tests/                     # Test suite
│   └── __init__.py
│
├── .gitignore
├── LICENSE
├── README.md
└── pyproject.toml
```

### 🏗️ Module Overview

#### `cli/` Package
- **`main.py`**: Command-line argument parsing and main entry point
- **`output.py`**: Console output formatting with colors and structured display

#### `core/` Package
- **`dns.py`**: DNS resolution utilities
  - MX record lookup with priority sorting
  - SPF record extraction from TXT records
  - DMARC record lookup at `_dmarc.domain`
- **`sender.py`**: Email sending logic
  - Direct SMTP connection to MX servers
  - STARTTLS support
  - Error classification and handling

#### `models/` Package
- **`config.py`**: Email configuration with validation
- **`result.py`**: Test result and DNS information models

#### `utils/` Package
- **`constants.py`**: Error types, output formats, timeouts
- **`exceptions.py`**: Custom exception classes

## 🔧 Technical Details

### How It Works

1. **DNS Resolution**
   - Resolves MX records for recipient's domain
   - Fetches SPF and DMARC records for sender's domain
   - Determines sender's public IP address

2. **Direct SMTP Connection**
   - Connects directly to MX server on port 25
   - Sends EHLO with local hostname
   - Attempts STARTTLS if available
   - Delivers email without authentication

3. **Error Analysis**
   - Parses SMTP response codes
   - Classifies rejection reasons
   - Provides actionable explanations

### SMTP Flow

```
Client                          MX Server
  |                                 |
  |-------- TCP Connect :25 ------->|
  |<-------- 220 Welcome -----------|
  |-------- EHLO hostname --------->|
  |<-------- 250 Extensions --------|
  |-------- STARTTLS -------------->|
  |<-------- 220 Ready -------------|
  |======== TLS Handshake =========|
  |-------- EHLO hostname --------->|
  |-------- MAIL FROM: ------------>|
  |<-------- 250 OK ----------------|
  |-------- RCPT TO: -------------->|
  |<-------- 250 OK ----------------|
  |-------- DATA ------------------>|
  |-------- [Message] ------------->|
  |-------- . --------------------->|
  |<-------- 250 OK / 550 Reject ---|
  |-------- QUIT ------------------>|
```

### Error Types

| Error Type | SMTP Code | Description |
|------------|-----------|-------------|
| `SUCCESS` | 250 | Email accepted |
| `SPF_FAIL` | 550/5.7.1 | SPF validation failed |
| `NO_PTR_RECORD` | 550/5.7.25 | Missing reverse DNS |
| `DMARC_FAIL` | 550 | DMARC policy rejection |
| `SPAM_DETECTED` | 550/5.7.0 | Spam classification |
| `SENDER_REFUSED` | 550 | Sender rejected |
| `RECIPIENT_REFUSED` | 550 | Invalid recipient |
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
- ✅ **Security Audits** - Assess email authentication posture
- ✅ **Penetration Testing** - Authorized email security assessments
- ✅ **Configuration Verification** - Confirm DNS records are working
- ⚠️ **Phishing Simulation** - Only with proper authorization

## 💬 Support

For more information and support:

- 🐛 **Issues**: [Create an issue on GitHub](https://github.com/SmookeyDev/spfspoofer/issues)
- 💡 **Feature Requests**: Submit via GitHub issues
- 📚 **SPF Documentation**: [RFC 7208](https://tools.ietf.org/html/rfc7208)
- 📚 **DMARC Documentation**: [RFC 7489](https://tools.ietf.org/html/rfc7489)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Developed with ❤️ by **SmookeyDev**

