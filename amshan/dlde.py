"""Direct Local Data Exchange of Energy Meters module."""
from __future__ import annotations

import logging
from datetime import datetime
from re import Pattern
from re import compile as regex_compile
from typing import Optional, Tuple, cast

from amshan.common import MeterReaderBase
from amshan.obis import Obis

_LOGGER = logging.getLogger(__name__)

START_CHARACTER_HEX = 0x2F
END_CHARACTER_HEX = 0x21
LF_CHARACTER = 0x0A

_item_pattern: Pattern = regex_compile(
    r"^(?P<obis>.*)\(\s*(?P<value>[^\*]+)(\*(?P<unit>[a-zA-Z]+))?\)\s*$"
)

P1ReadoutElement = Tuple[str, str, Optional[str]]
"""P1 readout element."""


class DataReadout:
    """Mode D data readout."""

    def __init__(self, readout: bytes) -> None:
        """Initialize DataReadout."""
        self._readout = readout
        if readout[0] != START_CHARACTER_HEX:
            raise ValueError("Readout must start with '/' character.")

        self._end_pos = readout.find(END_CHARACTER_HEX)
        if self._end_pos == -1:
            raise ValueError(
                "Readout must have an end line starting with '!' character."
            )

        self._data_pos = readout.find(LF_CHARACTER) + 1
        if self._data_pos < 1:
            raise ValueError("Data not found.")

    def __len__(self) -> int:
        """Length of readout bytes."""
        return len(self._readout)

    @property
    def readout_bytes(self) -> bytes:
        """Return raw data."""
        return bytes(self._readout)

    @property
    def identification_line(self) -> str:
        """Identification line (first line of data readout)."""
        return self._readout[: self._data_pos].decode("ascii").strip()

    @property
    def end_line(self) -> str:
        """End line (last line of data readout)."""
        return self._readout[self._end_pos :].decode("ascii").strip()

    @property
    def data(self) -> bytes:
        """Return raw data."""
        return bytes(self._readout[self._data_pos : self._end_pos])

    @property
    def data_lines(self) -> list[str]:
        """Return data lines."""
        data = self._readout[self._data_pos : self._end_pos]
        return [line for line in data.decode("ascii").splitlines() if len(line.strip())]

    def __str__(self) -> str:
        """Return readout as text."""
        return self._readout.decode("ascii")

    def __repr__(self) -> str:
        """Return the “official” string representation."""
        return str(self)


class ModeDReader(MeterReaderBase[DataReadout]):
    """Direct Local Data Exchange mode D data reader."""

    def __init__(self) -> None:
        """Initialize ModeDReader."""
        self._buffer = _ReaderBuffer()
        self._raw_data = bytearray()
        self._is_int_hunt_mode = True

    @property
    def is_in_hunt_mode(self) -> bool:
        """Return True when reader is hunting for start of readout."""
        return self._is_int_hunt_mode

    def read(self, data_chunk: bytes) -> list[DataReadout]:
        """
        Call this function to read chunks of bytes.

        :param data_chunk: next bytes to parsed.
        :return: readout when a readout is complete (both with correct and incorrect checksum).
        """
        readouts_received: list[DataReadout] = []

        self._buffer.extend(data_chunk)

        if self._is_int_hunt_mode:
            self._buffer.trim_buffer_to_flag_or_end()

        while True:
            line = self._buffer.pop()
            if line is None:
                return readouts_received

            if self.is_in_hunt_mode:
                if line[0] == START_CHARACTER_HEX:
                    _LOGGER.debug("Start character in hunt mode.")
                    self._is_int_hunt_mode = False
                    self._raw_data.extend(line)
            else:
                self._raw_data.extend(line)
                if line[0] == END_CHARACTER_HEX:
                    readout = DataReadout(bytes(self._raw_data))
                    readouts_received.append(readout)
                    _LOGGER.debug("Readout received:\n%s", readout)
                    self._raw_data.clear()
                    self._is_int_hunt_mode = True


class _ReaderBuffer:
    """Buffer class used by ModeDReader."""

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._buffer_pos = 0

    def pop(self) -> bytearray | None:
        """Pop one line from buffer."""
        if len(self._buffer) > self._buffer_pos:
            lf_pos = self._buffer.find(LF_CHARACTER, self._buffer_pos)
            if lf_pos >= 0:
                line = self._buffer[self._buffer_pos : lf_pos + 1]
                self._buffer_pos += len(line)
                return line

        return None

    def extend(self, data_chunk: bytes) -> None:
        """Add bytes to buffer."""
        self._buffer.extend(data_chunk)

    def trim_buffer_to_current_position(self) -> None:
        """Trim buffer to current position."""
        self._buffer = self._buffer[self._buffer_pos :]
        self._buffer_pos = 0

    def trim_buffer_to_flag_or_end(self) -> None:
        """Trim buffer to start character or end of buffer."""
        self.trim_buffer_to_current_position()
        flag_pos = self._buffer.find(START_CHARACTER_HEX)
        if flag_pos == -1:
            # start character not found
            self._buffer.clear()
        if flag_pos > 0:
            # trim data before flag sequence
            self._buffer = self._buffer[flag_pos:]
        self._buffer_pos = 0


def _parse_p1_datetime(value: str) -> datetime:
    """Parse P1 date time string to datetime."""
    return datetime(
        2000 + int(value[0:2]),
        int(value[2:4]),
        int(value[4:6]),
        int(value[6:8]),
        int(value[8:10]),
        int(value[10:12]),
    )


def parse_p1_readout(
    readout: DataReadout,
) -> list[P1ReadoutElement]:
    """Parse data readout."""
    items: list[P1ReadoutElement] = []
    for line in readout.data_lines:
        match = _item_pattern.match(line)
        if match is None:
            raise ValueError(f"Data line '{line}' is not a valid line.")
        items.append(cast(P1ReadoutElement, match.group("obis", "value", "unit")))

    return items


def decode_p1_readout(readout: DataReadout) -> dict[str, str | int | float | datetime]:
    """Decode P1 readout into dictionary."""
    decoded: dict[str, str | int | float | datetime] = {}

    parsed = parse_p1_readout(readout)
    for item in parsed:
        obis = Obis.from_string(item[0])
        value: str | int | float | datetime | None = None
        unit = item[2]
        if unit and unit.lower() in ("kw", "kwh", "kvar", "kvarh", "v", "a"):
            value = float(item[1])
        else:
            if obis.to_group_cdr_str() == "1.0.0":
                value = _parse_p1_datetime(item[1])
            else:
                value = item[1]

        decoded[obis.to_group_cdr_str()] = value

    return decoded
