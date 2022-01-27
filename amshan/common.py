"""Common types use dby other modules."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")  # pylint: disable=invalid-name


class MeterReaderBase(ABC, Generic[T]):
    """Abstract base class for meter reader types."""

    @abstractmethod
    def read(self, data_chunk: bytes) -> list[T]:
        """
        Call this function feed reader with chunks of bytes.

        :param data_chunk: next bytes to parsed.
        :return: complete messages received
        """
