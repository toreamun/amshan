"""Use this module to Wired M-Bus profile HDLC frames."""
from __future__ import annotations

import logging

from han.common import MeterMessageBase, MeterMessageType, MeterReaderBase

_LOGGER = logging.getLogger(__name__)

FRAME_START: int = 0x68
FRAME_END: int = 0x16


class LongFrame(MeterMessageBase):
    """Wired M-Bus profile HDLC frame."""

    # Long Frame
    # With the long frame, after the start character 68h, the length field
    # (L field) is first transmitted twice, followed by the start character once
    # again. After this, there follow the function field (C field), the address
    # field (A field) and the control information field (CI field). The L field
    # gives the quantity of the user data inputs plus 3 (for C,A,CI). After the
    # user data inputs, the check sum is transmitted, which is built up over the
    # same area as the length field, and in conclusion the stop character 16h
    # is transmitted.

    def __init__(self, buffer: bytearray) -> None:
        """Construct Wired M-Bus HdlcFrame."""
        self._frame_data = buffer
        if len(buffer) <= 6:
            raise ValueError("To short to be a Long Frame.")
        if buffer[0] != FRAME_START:
            raise ValueError(f"Frame must start with {hex(FRAME_START)}")
        if buffer[3] != FRAME_START:
            raise ValueError(f"Frame have {hex(FRAME_START)} in 4th position.")
        if buffer[len(buffer) - 1] != FRAME_END:
            raise ValueError(f"Frame must end with {hex(FRAME_END)}")

    @property
    def message_type(self) -> MeterMessageType:
        """Return MeterMessageType of message."""
        return MeterMessageType.WIRED_MB_HDLC

    @property
    def is_valid(self) -> bool:
        """Return True when valitation (checksum etc.) is successfull."""
        return self._calculate_cheksum() == self.cheksum_field

    @property
    def as_bytes(self) -> bytes:
        """Return frame data bytes."""
        return bytes(self._frame_data)

    @property
    def payload(self) -> bytes:
        """Frame payload as bytes."""
        return bytes(self._frame_data[7:-2])

    @property
    def len_field(self) -> int:
        """Frame payload as bytes."""
        return self._frame_data[1]

    @property
    def cheksum_field(self) -> int:
        """Frame payload as bytes."""
        return self._frame_data[len(self._frame_data) - 2]

    @property
    def function_field(self) -> int:
        """Get function field (C)."""
        return self._frame_data[4]

    @property
    def address_field(self) -> int:
        """Get address field (A)."""
        return self._frame_data[5]

    @property
    def controll_info_field(self) -> int:
        """Get control information field (CI)."""
        return self._frame_data[6]

    def _calculate_cheksum(self) -> int:
        total = 0
        for byte in self._frame_data[4:-2]:
            total = total + byte
        return total % 256


class FrameReader(MeterReaderBase[LongFrame]):
    """Use this class to read Wired M-Bus profile HDLC-frames as stream of bytes."""

    def __init__(self) -> None:
        """Initialize FrameReader."""
        self._raw_data = bytearray()
        self._buffer = bytearray()
        self._is_int_hunt_mode = True

    @property
    def is_in_hunt_mode(self) -> bool:
        """Return True when reader is hunting for start of frame."""
        return True

    @staticmethod
    def find_frame(buffer: bytes, start: int = 0) -> tuple[int, int]:
        """Search for complete frame in buffer."""
        while start < len(buffer) - 9:
            start_pos = buffer.find(FRAME_START, start)
            if start_pos < 0:
                break
            start = start_pos + 1

            if (
                len(buffer) > start_pos + 3
                and buffer[start_pos + 3] == FRAME_START
                and buffer[start_pos + 1] == buffer[start_pos + 2]
            ):
                pos = start_pos + 4 + 2
                data_sum = 0
                while pos < len(buffer):
                    data_sum = data_sum + buffer[pos - 2]
                    if buffer[pos] == FRAME_END:
                        calculated_cheksum = data_sum % 256
                        cheksum = buffer[pos - 1]
                        if calculated_cheksum == cheksum:
                            return (start_pos, pos)
                    pos = pos + 1

        return (-1, -1)

    def read(self, data_chunk: bytes) -> list[LongFrame]:
        """
        Call this function to read chunks of bytes.

        :param data_chunk: next bytes to parsed.
        :return: frame when a frame is complete (both with correct and incorrect checksum).
        """
        frames_received: list[LongFrame] = []

        # if self.is_in_hunt_mode:
        #     flag_pos = data_chunk.find(FRAME_START)
        #     if flag_pos >= 0:
        #         # trim data before flag sequence
        #         self._buffer.extend(data_chunk[flag_pos:])
        # else:
        self._buffer.extend(data_chunk)

        max_end = 0
        start = 0
        while start >= 0:
            start, end = FrameReader.find_frame(self._buffer, start)
            if end > 0:
                max_end = end
                frame = LongFrame(self._buffer[start : end + 1])
                frames_received.append(frame)
                start = end

        if max_end > 0:
            # trim buffer start
            self._buffer = self._buffer[max_end + 1 :]

        return frames_received
