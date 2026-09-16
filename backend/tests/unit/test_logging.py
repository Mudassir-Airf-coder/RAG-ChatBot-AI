from app.logging import get_logger, configure_logging


def test_api_key_redacted(capsys):
    """API key is redacted in log output."""
    configure_logging("INFO")
    logger = get_logger("test")
    logger.info("test_event", api_key="sk-fake-12345")
    captured = capsys.readouterr()
    assert "sk-fake-12345" not in captured.out
    assert "***REDACTED***" in captured.out


def test_multiple_sensitive_keys_redacted(capsys):
    """Multiple sensitive keys are redacted."""
    configure_logging("INFO")
    logger = get_logger("test")
    logger.info(
        "auth_test",
        api_key="sk-abc",
        authorization="Bearer tok-xyz",
        token="my-token",
        password="secret123",
    )
    captured = capsys.readouterr()
    assert "sk-abc" not in captured.out
    assert "tok-xyz" not in captured.out
    assert "my-token" not in captured.out
    assert "secret123" not in captured.out
    assert captured.out.count("***REDACTED***") == 4


def test_non_sensitive_keys_preserved(capsys):
    """Non-sensitive keys are preserved in logs."""
    configure_logging("INFO")
    logger = get_logger("test")
    logger.info("normal_event", user_id="user-123", action="upload")
    captured = capsys.readouterr()
    assert "user-123" in captured.out
    assert "upload" in captured.out
