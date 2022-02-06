"""Common types use dby other modules."""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Generic, TypeVar


class MeterMessageType(Enum):
    """Meter message type."""

    UNKNOWN = auto()
    HDLC_DLMS = auto()
    DLMS = auto()
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


class DlmsMessage(MeterMessageBase):
    """Message containing DLMS (binary) message without HDLC framing."""

    def __init__(self, binary: bytes) -> None:
        """Initialize DlmsMessage."""
        super().__init__()
        self._binary: bytes = binary

    @property
    def message_type(self) -> MeterMessageType:
        """Return MeterMessageType (DLMS) of message."""
        return MeterMessageType.DLMS

    @property
    def is_valid(self) -> bool:
        """Return True when minimum length is fulfilled."""
        return len(self._binary) > 4

    @property
    def as_bytes(self) -> bytes | None:
        """Message as data."""
        return self._binary

    @property
    def payload(self) -> bytes | None:
        """Return None for stop message."""
        return self._binary


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
