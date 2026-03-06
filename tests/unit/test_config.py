"""Unit tests for the configuration module of eq_cims_management_ui."""

import pytest

from eq_cims_management_ui.config.config import (
    DefaultConfig,
    DeployedConfig,
    ProdConfig,
    get_config,
)


@pytest.mark.parametrize(
    "env_value,expected_class",
    [
        ("dev", DeployedConfig),
        ("staging", DeployedConfig),
        ("prod", ProdConfig),
        (None, DefaultConfig),
        ("unknown", DefaultConfig),
    ],
)
def test_correct_config_class_selected(monkeypatch, env_value, expected_class):
    """Test that the correct configuration class is selected based on the environment variable."""
    if env_value is not None:
        monkeypatch.setenv("RUNTIME_ENVIRONMENT", env_value)
    else:
        monkeypatch.delenv("RUNTIME_ENVIRONMENT", raising=False)

    config = get_config()
    assert isinstance(config, expected_class)
