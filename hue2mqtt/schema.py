"""Schemas for data about lights."""
from datetime import datetime
from typing import Any, List, Optional, Tuple, Union

from pydantic import BaseModel, Field


class LightBaseState(BaseModel):
    """The base attributes of a light state."""

    on: Optional[bool]

    alert: Optional[str]
    bri: Optional[int]
    ct: Optional[int]
    effect: Optional[str]
    hue: Optional[int]
    sat: Optional[int]
    xy: Optional[Tuple[int, int]]
    transitiontime: Optional[str]


class LightSetState(LightBaseState):
    """The settable states of a light."""

    bri_inc: Optional[int]
    sat_inc: Optional[int]
    hue_inc: Optional[int]
    ct_inc: Optional[int]
    xy_inc: Optional[int]


class GroupSetState(LightSetState):
    """The settable states of a group."""

    scene: Optional[str]


class LightState(LightBaseState):
    """The State of a light that we can read."""

    reachable: Optional[bool]
    color_mode: Optional[str]
    mode: Optional[str]


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

    group_class: Optional[str] = Field(default=None, alias="class")

    action: LightState


class GenericSensorState(BaseModel):
    """Information about the state of a sensor."""

    lastupdated: datetime


class PresenceSensorState(GenericSensorState):
    """Information about the state of a sensor."""

    presence: bool


class RotarySensorState(GenericSensorState):
    """Information about the state of a sensor."""

    rotaryevent: str
    expectedrotation: str
    expectedeventduration: str


class SwitchSensorState(GenericSensorState):
    """Information about the state of a sensor."""

    buttonevent: Optional[int]


class LightLevelSensorState(GenericSensorState):
    """Information about the state of a sensor."""

    dark: bool
    daylight: bool
    lightlevel: int


class TemperatureSensorState(GenericSensorState):
    """Information about the state of a sensor."""

    temperature: int


class HumiditySensorState(GenericSensorState):
    """Information about the state of a sensor."""

    humidity: int


class OpenCloseSensorState(GenericSensorState):
    """Information about the state of a sensor."""

    open: str


SensorState = Union[
    PresenceSensorState,
    RotarySensorState,
    SwitchSensorState,
    LightLevelSensorState,
    TemperatureSensorState,
    HumiditySensorState,
    OpenCloseSensorState,
]


class SensorInfo(BaseModel):
    """Information about a sensor."""

    id: int
    name: str
    type: str
    modelid: str
    manufacturername: str

    productname: str
    uniqueid: str
    swversion: Optional[str]

    state: SensorState
    capabilities: Any
