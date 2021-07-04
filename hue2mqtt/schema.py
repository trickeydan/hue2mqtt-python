"""Schemas for data about lights."""
from typing import List, Optional, Tuple

from pydantic import BaseModel, Field


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


class GroupState(BaseModel):
    """The state of lights in a group."""

    all_on: bool
    any_on: bool


class GroupInfo(BaseModel):
    """Information about a light group."""

    id: int
    name: str
    lights: List[int]
    sensors: List[int]
    type: str
    state: GroupState

    group_class: str = Field(..., alias="class")

    action: LightState
