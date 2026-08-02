"""Tests for configuration settings loading and validation."""

from app.core.config import Settings


def test_settings_default_values() -> None:
    """Test that settings load with correct defaults."""
    custom_settings = Settings()
    assert custom_settings.PROJECT_NAME == "CogMesh Runtime Engine"
    assert custom_settings.API_V1_STR == "/api/v1"
    assert custom_settings.PORT == 8000
    assert custom_settings.DEBUG is True


def test_log_level_validator() -> None:
    """Test that log level string is correctly parsed and normalized."""
    s = Settings(LOG_LEVEL="debug")
    assert s.LOG_LEVEL == "DEBUG"

    invalid_s = Settings(LOG_LEVEL="NON_EXISTENT")
    assert invalid_s.LOG_LEVEL == "INFO"
