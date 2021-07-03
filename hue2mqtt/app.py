"""Application entrypoint."""
import asyncio
from typing import Optional

import click

from .discovery import discover_bridge
from .hue2mqtt import Hue2MQTT

loop = asyncio.get_event_loop()


@click.command("hue2mqtt")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
@click.option("--discover", is_flag=True)
def app(*, verbose: bool, config_file: Optional[str], discover: bool) -> None:
    """Main function for Hue2MQTT."""
    if discover:
        loop.run_until_complete(discover_bridge())
    else:
        # Start application
        hue2mqtt = Hue2MQTT(verbose, config_file)
        loop.run_until_complete(hue2mqtt.run())


if __name__ == "__main__":
    app()
