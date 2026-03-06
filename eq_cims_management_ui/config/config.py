"""Configuration for the EQ CIR Management UI application."""

from __future__ import annotations

import os


class DefaultConfig:  # pylint: disable=too-few-public-methods
    """The default application config."""

    LOG_FORMAT = os.environ.get("LOG_FORMAT", "JSON")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    CDN_URL = os.getenv("CDN_URL", "https://cdn.ons.gov.uk")
    SESSION_COOKIE_SECURE = False


class DeployedConfig(DefaultConfig):  # pylint: disable=too-few-public-methods
    """Configuration for the STAGING environment.

    Extends DEFAULT Config.
    """

    LOG_FORMAT = "JSON"


class ProdConfig(DeployedConfig):  # pylint: disable=too-few-public-methods
    """Configuration for the UAT and PROD environment.

    Extends DEPLOYED Config.
    Further configuration will be added when needed
    """


def get_config() -> DefaultConfig | DeployedConfig | ProdConfig:
    """Return the correct config class based on environment."""
    env = os.environ.get("RUNTIME_ENVIRONMENT", "").lower()

    match env:
        case "dev" | "staging":
            return DeployedConfig()
        case "prod":
            return ProdConfig()
        case _:
            return DefaultConfig()


# Use in application startup
config = get_config()
