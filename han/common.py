"""Common types use dby other modules."""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Generic, TypeVar


class MeterMessageType(Enum):
    """Meter message type."""

    HDLC_DLMS = auto()
    P1 = auto()


class MeterMessageBase(ABC):
    """Abstract base class for meter messages."""

    @property
    @abstractmethod
    def message_type(self) -> MeterMessageType:
        """Return MeterMessageType of message."""

    @property
    @abstractmethod
    def is_valid(self) -> bool:
        """Return True when valitation (checksum etc.) is successfull."""

    @property
    @abstractmethod
    def as_bytes(self) -> bytes | None:
        """Message as data."""

    @property
    @abstractmethod
    def payload(self) -> bytes | None:
        """Payload field."""


TMessage = TypeVar("TMessage", bound=MeterMessageBase)  # pylint: disable=invalid-name


class MeterReaderBase(ABC, Generic[TMessage]):
    """Abstract base class for meter reader types."""

    @property
    @abstractmethod
    def is_in_hunt_mode(self) -> bool:
        """Return True when reader is hunting for start of message."""

    @abstractmethod
    def read(self, data_chunk: bytes) -> list[TMessage]:
        """
        Call this function feed reader with chunks of bytes.

        :param data_chunk: next bytes to parsed.
        :return: complete messages received
        """
