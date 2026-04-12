# Security Policy

## Reporting a Vulnerability
**Please do not open a public GitHub issue for security vulnerabilities.**

To report a vulnerability, please use GitHub's **Private Vulnerability Reporting** system. This keeps the report confidential between you and the maintainers until a fix is released. To use this:

1. Navigate to the **Security** tab of this repository.
2. Click on **Advisories** on the left sidebar.
3. Click **Report a vulnerability**.

We aim to acknowledge all reports within 48 hours.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Main    | ✅ Yes             |
| < 1.0   | ❌ No              |

## RAG & Docker Security
- **API Keys**: Ensure your `GROQ_API_KEY` is kept in a `.env` file and never committed.
- **Data Privacy**: This project runs locally. Ensure your Docker network is not exposed to the public internet if processing sensitive PDFs.
