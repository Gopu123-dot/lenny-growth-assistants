"""Automated security tests for iframe sandboxing, credential sanitization, and grounding."""

import re
from pathlib import Path
from app.core.logging import sanitize_data


def test_log_credential_sanitization():
    payload = {
        "api_key": "sk-ant-api03-secret-key-12345",
        "authorization": "Bearer secret-token-xyz",
        "nested": {
            "password": "supersecretpassword",
            "normal_field": "public_data",
        }
    }
    sanitized = sanitize_data(payload)
    assert sanitized["api_key"] == "[REDACTED]"
    assert sanitized["authorization"] == "[REDACTED]"
    assert sanitized["nested"]["password"] == "[REDACTED]"
    assert sanitized["nested"]["normal_field"] == "public_data"


def test_frontend_iframe_sandbox_policy():
    """Verifies that the Artifact Viewer iframe in index.html enforces strict sandbox attributes."""
    index_path = Path(__file__).resolve().parent.parent.parent / "frontend" / "index.html"
    assert index_path.exists(), "frontend/index.html must exist"

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Find the iframe tag
    match = re.search(r"<iframe[^>]*>", html, re.IGNORECASE)
    assert match, "Iframe must be present in frontend/index.html"
    iframe_tag = match.group(0)

    # Must contain sandbox="allow-scripts"
    assert 'sandbox="allow-scripts"' in iframe_tag or "sandbox='allow-scripts'" in iframe_tag

    # Must NOT permit allow-same-origin (preventing access to parent cookies and localStorage)
    assert "allow-same-origin" not in iframe_tag

    # Must NOT permit allow-top-navigation (preventing malicious redirects)
    assert "allow-top-navigation" not in iframe_tag
