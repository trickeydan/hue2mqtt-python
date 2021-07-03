"""
MQTT Topic Abstraction.

Allows topic strings to be constructed, along with regex to match them.
"""

from re import compile
from typing import Dict, Match, Optional, Pattern, Sequence


class Topic:
    """
    An MQTT Topic.

    A topic that may be published or subscribed to.
    """

    WILDCARDS: Dict[str, str] = {
        "+": "([^/]+)",
        "#": "(.+)",
    }

    def __init__(self, parts: Sequence[str]) -> None:
        self.parts = parts

    def match(self, topic: str) -> Optional[Match[str]]:
        """Perform a regex match on a topic."""
        return self.regex.match(topic)

    @classmethod
    def parse(cls, topic: str) -> 'Topic':
        """
        Parse a string topic into a Topic instance.

        It is assumed that the supplied topic complies with the MQTT spec.
        If not, then behaviour is undefined.
        """
        if len(topic) > 1:
            if topic[:1] == "/" or topic[-1:] == "/":
                raise ValueError("Topic cannot begin or end with /")
        else:
            if topic == "/" or len(topic) == 0:
                raise ValueError("Invalid Topic")

        return cls(topic.split("/"))

    def __str__(self) -> str:
        return "/".join(str(p) for p in self.parts)

    def __repr__(self) -> str:
        return f"Topic(\"{self}\")"

    def __hash__(self) -> int:
        return hash(repr(self))

    def __eq__(self, other: object) -> bool:
        try:
            return self.parts == other.parts  # type: ignore
        except AttributeError:
            return False

    @property
    def is_publishable(self) -> bool:
        """
        Determine if it is valid to publish to this topic.

        We are not permitting publication to topics containing wildcards.
        """
        return all(x not in self.parts for x in self.WILDCARDS)

    @property
    def regex(self) -> Pattern[str]:
        """
        Regular expression to match the topic.

        Any wildcard fields are available as capture groups.
        """
        handled_parts = []
        for p in self.parts:
            try:
                handled_parts.append(self.WILDCARDS[p])
            except KeyError:
                handled_parts.append(p)

        return compile("^" + "/".join(handled_parts) + "$")
