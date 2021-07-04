"""Schemas for MQTT Messages."""
from typing import Optional

from pydantic import BaseModel


class BridgeInfo(BaseModel):
    """Information about the Hue Bridge."""

    name: str
    mac_address: str
    api_version: str


class Hue2MQTTStatus(BaseModel):
    """Status of Hue2MQTT."""

    online: bool
    bridge: Optional[BridgeInfo] = None
