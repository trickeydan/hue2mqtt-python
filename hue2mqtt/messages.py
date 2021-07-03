"""Schemas for MQTT Messages."""
from typing import Dict, Optional

from pydantic import BaseModel

from .light import LightInfo


class BridgeInfo(BaseModel):
    """Information about the Hue Bridge."""

    name: str
    mac_address: str
    api_version: str

    lights: Dict[int, LightInfo]


class Hue2MQTTStatus(BaseModel):
    """Status of Hue2MQTT."""

    online: bool
    bridge: Optional[BridgeInfo] = None
