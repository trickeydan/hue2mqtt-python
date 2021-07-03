"""Test that the hue2mqtt imports as expected."""

import hue2mqtt


def test_module() -> None:
    """Test that the module behaves as expected."""
    assert hue2mqtt.__version__ is not None
