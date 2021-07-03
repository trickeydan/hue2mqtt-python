"""Hue Bridge Discovery and Configuration."""

import sys

import aiohttp
from aiohue.discovery import discover_nupnp
from aiohue.errors import LinkButtonNotPressed


async def discover_bridge() -> None:
    """Discover Hue Bridge and get username."""
    print("Searching for local bridges.")

    async with aiohttp.ClientSession() as session:
        bridges = await discover_nupnp(session)

        if len(bridges) != 1:
            print(f"Error: expected to find exactly 1 bridge, found {len(bridges)}")
            sys.exit(1)
        else:
            bridge = bridges[0]
            print("Found bridge at", bridge.host)
            try:
                await bridge.create_user("hue2mqtt")
                print("Your username is", bridge.username)
                print("Please add these details to hue2mqtt.toml")
            except LinkButtonNotPressed:
                print("Error: Press the link button on the bridge before running discovery")  # noqa: E501
                sys.exit(1)
