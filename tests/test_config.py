"""Test that we can load config files."""

from pathlib import Path

from hue2mqtt.config import Hue2MQTTConfig

DATA_DIR = Path(__file__).resolve().parent.joinpath("data/configs")


def test_valid_config() -> None:
    """Test that we can load a valid config from a file."""
    with DATA_DIR.joinpath("valid.toml").open("rb") as fh:
        config = Hue2MQTTConfig.load_from_file(fh)
    assert config is not None
