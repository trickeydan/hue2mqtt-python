"""
Configuration schema for Astoria.

Common to all components.
"""
from pathlib import Path
from typing import IO, Optional

from pydantic import BaseModel

# Backwards compatibility for TOML in stdlib from Python 3.11
try:
    import tomllib  # type: ignore[import]
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]


class HueBridgeInfo(BaseModel):
    """MQTT Broker Information."""

    ip: str
    username: str

    class Config:
        """Pydantic config."""

        extra = "forbid"


class MQTTBrokerInfo(BaseModel):
    """MQTT Broker Information."""

    host: str
    port: int
    enable_auth: bool = False
    username: str = ""
    password: str = ""
    enable_tls: bool = False
    topic_prefix: str = "hue2mqtt"
    force_protocol_version_3_1: bool = False

    class Config:
        """Pydantic config."""

        extra = "forbid"


class Hue2MQTTConfig(BaseModel):
    """Config schema for Hue2MQTT."""

    mqtt: MQTTBrokerInfo
    hue: HueBridgeInfo

    class Config:
        """Pydantic config."""

        extra = "forbid"

    @classmethod
    def _get_config_path(cls, config_str: Optional[str] = None) -> Path:
        """Check for a config file or search the filesystem for one."""
        CONFIG_SEARCH_PATHS = [
            Path("hue2mqtt.toml"),
            Path("/etc/hue2mqtt.toml"),
        ]
        if config_str is None:
            for path in CONFIG_SEARCH_PATHS:
                if path.exists() and path.is_file():
                    return path
        else:
            path = Path(config_str)
            if path.exists() and path.is_file():
                return path
        raise FileNotFoundError("Unable to find config file.")

    @classmethod
    def load(cls, config_str: Optional[str] = None) -> 'Hue2MQTTConfig':
        """Load the config."""
        config_path = cls._get_config_path(config_str)
        with config_path.open("rb") as fh:
            return cls.load_from_file(fh)

    @classmethod
    def load_from_file(cls, fh: IO[bytes]) -> 'Hue2MQTTConfig':
        """Load the config from a file."""
        return cls(**tomllib.load(fh))
