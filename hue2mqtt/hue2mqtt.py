"""
Data Component base class.

A data component represents the common functionality between
State Managers and Consumers. It handles connecting to the broker
and managing the event loop.
"""
import asyncio
import logging
import signal
import sys
from signal import SIGHUP, SIGINT, SIGTERM
from types import FrameType
from typing import Optional

import aiohttp
import aiohue
from aiohttp.client import ClientSession

from hue2mqtt import __version__
from hue2mqtt.light import LightInfo
from hue2mqtt.messages import BridgeInfo, Hue2MQTTStatus

from .config import Hue2MQTTConfig
from .mqtt.wrapper import MQTTWrapper

LOGGER = logging.getLogger(__name__)

loop = asyncio.get_event_loop()


class Hue2MQTT():
    """Hue to MQTT Bridge."""

    config: Hue2MQTTConfig

    def __init__(
        self,
        verbose: bool,
        config_file: Optional[str],
        *,
        name: str = "hue2mqtt",
    ) -> None:
        self.config = Hue2MQTTConfig.load(config_file)
        self.name = name

        self._setup_logging(verbose)
        self._setup_event_loop()
        self._setup_mqtt()

    def _setup_logging(self, verbose: bool, *, welcome_message: bool = True) -> None:
        if verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format=f"%(asctime)s {self.name} %(name)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format=f"%(asctime)s {self.name} %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            # Suppress INFO messages from gmqtt
            logging.getLogger("gmqtt").setLevel(logging.WARNING)

        if welcome_message:
            LOGGER.info(f"Hue2MQTT v{__version__} - {self.__doc__}")

    def _setup_event_loop(self) -> None:
        self._stop_event = asyncio.Event()

        loop.add_signal_handler(SIGHUP, self.halt)
        loop.add_signal_handler(SIGINT, self.halt)
        loop.add_signal_handler(SIGTERM, self.halt)

    def _setup_mqtt(self) -> None:
        self._mqtt = MQTTWrapper(
            self.name,
            self.config.mqtt,
            last_will=Hue2MQTTStatus(online=False),
        )

    def _exit(self, signals: signal.Signals, frame_type: FrameType) -> None:
        sys.exit(0)

    async def run(self) -> None:
        """Entrypoint for the data component."""
        await self._mqtt.connect()
        LOGGER.info("Connected to MQTT Broker")

        async with aiohttp.ClientSession() as websession:
            try:
                await self._setup_bridge(websession)
            except aiohue.errors.Unauthorized:
                LOGGER.error("Bridge rejected username. Please use --discover")
                self.halt()
                return
            await self._publish_bridge_info()
            await self.main(websession)

        LOGGER.info("Disconnecting from MQTT Broker")
        await self._publish_bridge_info(online=False)
        await self._mqtt.disconnect()

    def halt(self) -> None:
        """Stop the component."""
        LOGGER.info("Halting Hue2MQTT")
        self._stop_event.set()

    async def _setup_bridge(self, websession: ClientSession) -> None:
        """Connect to the Hue Bridge."""
        self._bridge = aiohue.Bridge(
            self.config.hue.ip,
            websession,
            username=self.config.hue.username,
        )
        LOGGER.info(f"Connecting to Hue Bridge at {self.config.hue.ip}")
        await self._bridge.initialize()

    async def _publish_bridge_info(self, *, online: bool = True) -> None:
        """Publish info about the Hue Bridge."""
        if online:
            LOGGER.info(f"Bridge Name: {self._bridge.config.name}")
            LOGGER.info(f"Bridge MAC: {self._bridge.config.mac}")
            LOGGER.info(f"API Version: {self._bridge.config.apiversion}")

            lights = {
                int(k): LightInfo(id=k, **v.raw)
                for k, v in self._bridge.lights._items.items()
            }

            for light in lights.values():
                light.state = None

            info = BridgeInfo(
                name=self._bridge.config.name,
                mac_address=self._bridge.config.mac,
                api_version=self._bridge.config.apiversion,
                lights=lights,
            )
            message = Hue2MQTTStatus(online=online, bridge=info)
        else:
            message = Hue2MQTTStatus(online=online)

        self._mqtt.publish("status", message)

    async def main(self, websession: ClientSession) -> None:
        """Main method of the data component."""
        await self._stop_event.wait()
