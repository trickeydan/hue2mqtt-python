"""Test the MQTT Wrapper class."""

import asyncio
from typing import Match

import gmqtt
import pytest
from pydantic import BaseModel

from hue2mqtt.config import MQTTBrokerInfo
from hue2mqtt.mqtt.topic import Topic
from hue2mqtt.mqtt.wrapper import MQTTWrapper

BROKER_INFO = MQTTBrokerInfo(
    host="localhost",
    port=1883,
)


class StubModel(BaseModel):
    """Test BaseModel."""

    foo: str


async def stub_message_handler(
    match: Match[str],
    payload: str,
) -> None:
    """Used in tests as a stub with the right type."""
    pass


def test_wrapper_init_minimal() -> None:
    """Test initialising the wrapper with minimal options."""
    wr = MQTTWrapper("foo", BROKER_INFO)

    assert wr._client_name == "foo"
    assert wr._last_will is None

    assert len(wr._topic_handlers) == 0

    assert wr._client._client_id == "foo"


def test_wrapper_is_connected_at_init() -> None:
    """Test that the wrapper is not connected to the broker at init."""
    wr = MQTTWrapper("foo", BROKER_INFO)
    assert not wr.is_connected


def test_wrapper_last_will_message_null() -> None:
    """Test that the last will message is None when not supplied."""
    wr = MQTTWrapper("foo", BROKER_INFO)
    assert wr.last_will_message is None


def test_wrapper_mqtt_prefix() -> None:
    """Test that the MQTT prefix is as expected."""
    wr = MQTTWrapper("foo", BROKER_INFO)
    assert wr.mqtt_prefix == "hue2mqtt"


def test_subscribe() -> None:
    """Test that subscribing works as expected."""
    wr = MQTTWrapper("foo", BROKER_INFO)

    assert len(wr._topic_handlers) == 0

    wr.subscribe("bees/+", stub_message_handler)
    assert len(wr._topic_handlers) == 1
    assert wr._topic_handlers[Topic(["hue2mqtt", "bees", "+"])] == stub_message_handler


@pytest.mark.filterwarnings("ignore")
@pytest.mark.asyncio
async def test_connect_disconnect() -> None:
    """Test that the wrapper can connect and disconnect from the broker."""
    wr = MQTTWrapper("foo", BROKER_INFO)
    await wr.connect()
    assert wr.is_connected

    await wr.disconnect()
    assert not wr.is_connected


@pytest.mark.asyncio
async def test_handler_called() -> None:
    """Test that subscription handlers are called correctly."""
    ev = asyncio.Event()

    async def test_handler(
        match: Match[str],
        payload: str,
    ) -> None:
        assert payload == "hive"
        ev.set()

    wr = MQTTWrapper("foo", BROKER_INFO)
    wr.subscribe("bees/+", test_handler)
    await wr.connect()

    # Manually call on_message
    res = await wr.on_message(
        wr._client,
        "hue2mqtt/bees/bar",
        b"hive",
        0,
        {},
    )
    assert res == gmqtt.constants.PubRecReasonCode.SUCCESS

    await asyncio.wait_for(ev.wait(), 0.1)

    await wr.disconnect()


@pytest.mark.asyncio
async def test_publish_send_and_receive() -> None:
    """Test that we can publish and receive a message."""
    ev = asyncio.Event()

    async def test_handler(
        match: Match[str],
        payload: str,
    ) -> None:
        ev.set()

    wr_sub = MQTTWrapper("foo", BROKER_INFO)
    wr_pub = MQTTWrapper("bar", BROKER_INFO)
    wr_sub.subscribe("bees/+", test_handler)
    await wr_sub.connect()
    await wr_pub.connect()

    wr_pub.publish("bees/foo", StubModel(foo="bar"))

    await asyncio.wait_for(ev.wait(), 0.5)

    await wr_sub.disconnect()
    await wr_pub.disconnect()


@pytest.mark.asyncio
async def test_publish_send_and_receive_on_self() -> None:
    """Test that we can publish and receive a message on it's own topic."""
    ev = asyncio.Event()

    async def test_handler(
        match: Match[str],
        payload: str,
    ) -> None:
        ev.set()

    wr_sub = MQTTWrapper("foo", BROKER_INFO)
    wr_pub = MQTTWrapper("bar", BROKER_INFO)
    wr_sub.subscribe("", test_handler)
    await wr_sub.connect()
    await wr_pub.connect()

    wr_pub.publish("", StubModel(foo="bar"))

    await asyncio.wait_for(ev.wait(), 0.5)

    await wr_sub.disconnect()
    await wr_pub.disconnect()


@pytest.mark.asyncio
async def test_publish_bad_topic_error() -> None:
    """Test that we cannot publish to an invalid topic."""
    wr_pub = MQTTWrapper("bar", BROKER_INFO)
    await wr_pub.connect()

    with pytest.raises(ValueError):
        wr_pub.publish("bees/+", StubModel(foo="bar"))

    with pytest.raises(ValueError):
        wr_pub.publish("bees/#", StubModel(foo="bar"))

    with pytest.raises(ValueError):
        wr_pub.publish("bees/", StubModel(foo="bar"))

    await wr_pub.disconnect()
