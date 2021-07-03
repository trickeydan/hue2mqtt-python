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

from hue2mqtt import __version__

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
        )

    def _exit(self, signals: signal.Signals, frame_type: FrameType) -> None:
        sys.exit(0)

    async def run(self) -> None:
        """Entrypoint for the data component."""
        await self._mqtt.connect()
        LOGGER.info("Connected to MQTT Broker")

        await self.main()

        LOGGER.info("Disconnecting from MQTT Broker")
        await self._mqtt.disconnect()

    def halt(self, *, silent: bool = False) -> None:
        """Stop the component."""
        if not silent:
            LOGGER.info("Halting")
        self._stop_event.set()

    async def main(self) -> None:
        """Main method of the data component."""
        async with aiohttp.ClientSession() as session:
            bridge = aiohue.Bridge(
                self.config.hue.ip,
                session,
                username=self.config.hue.username,
            )
            LOGGER.info(f"Connecting to Hue Bridge at {self.config.hue.ip}")
            try:
                await bridge.initialize()
            except aiohue.errors.Unauthorized:
                LOGGER.error("Bridge rejected username. Please use --discover")
                self.halt()
                return

            LOGGER.info(f"Bridge Name: {bridge.config.name}")
            LOGGER.info(f"Bridge MAC: {bridge.config.mac}")
            LOGGER.info(f"API Version: {bridge.config.apiversion}")

            await self._stop_event.wait()
