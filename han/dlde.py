"""Direct Local Data Exchange of Energy Meters (IEC 62056-21) module."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from re import Pattern
from re import compile as regex_compile
from typing import cast

from han import obis_map
from han.common import MeterMessageBase, MeterMessageType, MeterReaderBase
from han.obis import Obis

_LOGGER = logging.getLogger(__name__)

START_CHARACTER_HEX = 0x2F
END_CHARACTER_HEX = 0x21
LF_CHARACTER = 0x0A


_ident_pattern: Pattern = regex_compile(
    r"^\/(?P<MANID>[A-Z][A-Z][a-zA-Z])(?P<BAUDID>\d)((\\\w)*)(?P<ID>[ -~]{1,16})(\r\n)?$"
)


@dataclass
class DataSetValue:
    """Represent a data set value with optional unit."""

    value: str
    """Value: 32 printable characters maximum with the exception of (, ), *, / and !. """

    unit: str | None
    """Unit: 16 printable characters maximum except for (, ), / and !."""

    @classmethod
    def parse(cls, value: str) -> DataSetValue:
        """Parse from string."""
        pair = value.split("*")
        if len(pair) > 2:
            raise ValueError("Found multiple value unit separators (*).")
        if len(pair) == 2:
            return DataSetValue(pair[0], pair[1])
        return cls(pair[0], None)


@dataclass
class DataSet:
    """
    Readout dataset.

    To reduce the quantity of data, the address and/or the unit information and can be dispensed with,
    provided that an unambiguous correlation exists. For example, the identification code or the
    unit information is not necessary for a sequence of similar values (sequence of historical values)
    on condition that the evaluation unit can clearly establish the identification code and
    unit of the succeeding values from the first value of a sequence.
    """

    address: str
    """Identification number or address: 16 printable characters maximum with the exception of (, ), /, and !."""

    values: list[DataSetValue]
    """List of values."""

    @classmethod
    def parse_data_block(cls, data: str) -> list[DataSet]:
        """Parse data set line into list of data set."""

        def get_address_and_values(line: str, from_pos: int):
            address = None
            values: list[DataSetValue] = []

            address_end = line.find("(", from_pos)
            if address_end > from_pos:
                address = line[from_pos:address_end]
                from_pos = address_end

            while from_pos > 0:
                value_end_pos = line.find(")", from_pos)
                values.append(DataSetValue.parse(line[from_pos + 1 : value_end_pos]))
                from_pos = value_end_pos + 1

                if from_pos == len(line):  # end of line
                    from_pos = -1
                    break

                if line[from_pos] != "(":  # end of address element(s)
                    break

            return (from_pos if values else -1, address, values)

        items: list[DataSet] = []
        lines = [line for line in data.splitlines() if len(line.strip())]
        for data_line in lines:
            position = 0
            while position > -1:
                position, address, values = get_address_and_values(data_line, position)
                if values:
                    items.append(cls(address, values))

        return items


class Ident:
    """Identification message."""

    def __init__(self, ident_line: str) -> None:
        """Initialize Ident."""
        match = _ident_pattern.match(ident_line)
        if not match:
            raise ValueError("Not an Ident message.")
        self._match = match

    @property
    def manufacturer_id(self) -> str:
        """
        Manufacturer's identification (FLAG ID) comprising three letters.

        See https://www.dlms.com/flag-id/flag-id-list
        """
        return cast(str, self._match.group("MANID"))

    @property
    def identification(self) -> str:
        """Manufacturer specific identification."""
        return cast(str, self._match.group("ID"))

    @staticmethod
    def is_ident_line(line: str) -> bool:
        """Return true if line match ident pattern."""
        return bool(_ident_pattern.match(line))

    def __str__(self) -> str:
        """Return readout as text."""
        return self._match.string


class DataReadout(MeterMessageBase):
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

        self._calculated_crc = self._calculate_crc16()
        self._ident: Ident | None = None

    def __len__(self) -> int:
        """Length of readout bytes."""
        return len(self._readout)

    @property
    def message_type(self) -> MeterMessageType:
        """Return MeterMessageType of message."""
        return MeterMessageType.P1

    @property
    def is_valid(self) -> bool:
        """Return True when valitation (checksum etc.) is successfull."""
        expected_checksum = self.expected_checksum
        if expected_checksum:
            if self._calculated_crc != expected_checksum:
                _LOGGER.debug(
                    "Expected cheksum is 0x%x, but calculated is 0x%x",
                    expected_checksum,
                    self._calculated_crc,
                )
                return False
        try:
            self._ident = self.identification_line
        except ValueError:
            _LOGGER.debug("Invalid ident line: %s", self.identification_line)
            return False

        for char in self._readout[self._data_pos : self._end_pos]:
            if char > 0x80 or char == b"!":
                _LOGGER.debug("Invalid character 0x%x sin readout data.", char)
                return False

        return True

    @property
    def as_bytes(self) -> bytes:
        """Return raw data."""
        return bytes(self._readout)

    @property
    def payload(self) -> bytes:
        """Readout data block as bytes."""
        return bytes(self._readout[self._data_pos : self._end_pos])

    @property
    def identification_line(self) -> Ident:
        """Identification line (first line of data readout)."""
        if self._ident is None:
            self._ident = Ident(self._readout[: self._data_pos].decode("ascii").strip())
        return self._ident

    @property
    def end_line(self) -> str:
        """End line (last line of data readout)."""
        return self._readout[self._end_pos :].decode("ascii").strip()

    @property
    def expected_checksum(self) -> int | None:
        """Checksum from end line."""
        end = self.end_line
        if len(end) > 1:
            return int(end[1:].strip(), base=16)
        return None

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

    def _calculate_crc16(self) -> int:
        buf = self._readout[0 : self._end_pos + 1]
        crc = 0x0000
        for byte in buf:
            crc ^= byte
            for _ in range(8):
                if crc & 0x01:
                    crc >>= 1
                    crc ^= 0xA001  # CRC16 polynomial x16 + x15 + x2 +1
                else:
                    crc >>= 1
        return crc


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

        if len(self._buffer) > 8191:
            self._is_int_hunt_mode = True
            self._buffer.trim_buffer_to_flag_or_end()

        self._buffer.extend(data_chunk)

        if self._is_int_hunt_mode:
            self._buffer.trim_buffer_to_flag_or_end()

        while True:
            line = self._buffer.pop()
            if line is None:
                return readouts_received

            if self.is_in_hunt_mode:
                if line[0] == START_CHARACTER_HEX:
                    line_str = line.decode("ascii")
                    if Ident.is_ident_line(line_str):
                        _LOGGER.debug("Ident line found: %s", line_str)
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

    def __len__(self) -> int:
        """Bytes in buffer."""
        return len(self._buffer)

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
) -> list[DataSet]:
    """Parse data readout content."""
    return parse_p1_readout_content(readout.payload)


def parse_p1_readout_content(
    content: bytes,
) -> list[DataSet]:
    """Parse data readout content."""
    if not content.isascii():
        raise ValueError("Readout must be ascii.")
    return DataSet.parse_data_block(content.decode("ascii"))


def _decode_parsed(
    parsed: list[DataSet],
) -> dict[str, str | int | float | datetime]:
    decoded: dict[str, str | int | float | datetime] = {}

    for item in parsed:
        if len(item.values) == 1:
            obis = Obis.from_string(item.address)

            obis_group_cdr = obis.to_group_cdr_str()
            if obis_group_cdr in obis_map.obis_name_map:
                element_name = obis_map.obis_name_map[obis_group_cdr]
            else:
                element_name = obis_group_cdr

            value: str | int | float | datetime | None = None
            unit = item.values[0].unit.lower() if item.values[0].unit else None
            if unit in ("v", "a", "var", "varh"):
                value = float(item.values[0].value)
            elif unit in ("kw", "kwh", "kvar", "kvarh"):
                value = int(float(item.values[0].value) * 1000)
            else:
                if obis.to_group_cdr_str() == "1.0.0":
                    value = _parse_p1_datetime(item.values[0].value)
                else:
                    value = item.values[0].value

            decoded[element_name] = value

    return decoded


def decode_p1_readout_content(
    content: bytes,
) -> dict[str, str | int | float | datetime]:
    """Decode P1 readout content into dictionary."""
    parsed = parse_p1_readout_content(content)
    if not parsed:
        raise ValueError("Content cotains no readout data.")
    return _decode_parsed(parsed)


def decode_p1_readout(readout: DataReadout) -> dict[str, str | int | float | datetime]:
    """Decode P1 readout into dictionary."""
    data_sets = parse_p1_readout(readout)
    decoded = _decode_parsed(data_sets)

    decoded[
        obis_map.FIELD_METER_MANUFACTURER_ID
    ] = readout.identification_line.manufacturer_id
    decoded[obis_map.FIELD_METER_TYPE_ID] = readout.identification_line.identification

    return decoded
