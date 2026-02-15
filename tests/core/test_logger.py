"""Tests for logging redaction utilities."""

from core.logger import redact_secrets


def test_redact_secrets_masks_sensitive_dict_keys():
    payload = {
        "openai_api_key": "sk-test-super-secret-key",
        "safe_field": "hello",
    }

    redacted = redact_secrets(payload)

    assert redacted["openai_api_key"] != payload["openai_api_key"]
    assert redacted["safe_field"] == "hello"


def test_redact_secrets_masks_long_token_strings():
    raw = "abcdefghijklmnopqrstuvwxyz0123456789"

    redacted = redact_secrets(raw, key_hint="error")

    assert redacted != raw
    assert redacted.startswith("abcd")
    assert redacted.endswith("6789")
