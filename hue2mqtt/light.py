"""Schemas for data about lights."""
from typing import Optional, Tuple

from pydantic import BaseModel


class LightState(BaseModel):
    """The State of a light."""

    on: Optional[bool]
    reachable: Optional[bool]

    alert: Optional[str]
    bri: Optional[int]
    color_mode: Optional[str]
    ct: Optional[int]
    effect: Optional[str]
    hue: Optional[int]
    mode: Optional[str]
    sat: Optional[int]
    xy: Optional[Tuple[int, int]]
    transitiontime: Optional[str]


class LightInfo(BaseModel):
    """Information about a light."""

    id: int
    name: str
    uniqueid: str
    state: Optional[LightState]

    manufacturername: str
    modelid: str
    productname: str
    type: str

    swversion: str
