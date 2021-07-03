"""Application entrypoint."""
import asyncio
from typing import Optional

import click

from .hue2mqtt import Hue2MQTT

loop = asyncio.get_event_loop()


@click.command("hue2mqtt")
@click.option("-v", "--verbose", is_flag=True)
@click.option("-c", "--config-file", type=click.Path(exists=True))
def app(*, verbose: bool, config_file: Optional[str]) -> None:
    """Main function for Hue2MQTT."""
    hue2mqtt = Hue2MQTT(verbose, config_file)
    loop.run_until_complete(hue2mqtt.run())


if __name__ == "__main__":
    app()
