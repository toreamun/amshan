"""Compute or check checksum using a 16-bit Fast Frame Check Sequence (FCS) derived from RFC1662."""
from typing import List


def _compute_fcs_16_crc_table() -> List[int]:
    """Generate a FCS-16 table."""
    polynomial = 0x8408  # The FCS-16 generator polynomial: x**0 + x**5 + x**12 + x**16.
    crc_table = [] * 256
    for byte in range(256):
        crc = 0
        for _ in range(8):
            if (byte ^ crc) & 1:
                crc = (crc >> 1) ^ polynomial
            else:
                crc >>= 1
            byte >>= 1
        crc_table.append(crc)
    return crc_table


class FastFrameCheckSequence16:
    """16 bit Fast Frame Check Sequence (FCS)."""

    INIT_FCS_16 = 0xFFFF  # Initial FCS value
    GOOD_FCS_16 = 0xF0B8  # Good final FCS value

    fast_frame_check_crc_table = _compute_fcs_16_crc_table()

    def __init__(self) -> None:
        """Initialize FastFrameCheckSequence16."""
        self._crc_value = self.INIT_FCS_16

    @staticmethod
    def _next(crc: int, byte: int) -> int:
        """Calculate a new fcs CRC given the current CRC value and the new data."""
        crc_index = (crc ^ byte) & 0xFF
        return (crc >> 8) ^ FastFrameCheckSequence16.fast_frame_check_crc_table[
            crc_index
        ]

    def update(self, byte: int) -> int:
        """Update the calculated CRC value for the specified input data."""
        self._crc_value = self._next(self._crc_value, byte)
        return self._crc_value

    @property
    def is_good(self) -> bool:
        """
        Return True when data AND checksum has been processed with update(), and the checksum is correct.

        FCS was designed so that a particular pattern results
        when the FCS operation passes over the complemented FCS.  A good
        frame is indicated by this "good FCS" value
        """
        return self.GOOD_FCS_16 == self._crc_value

    @property
    def checksum(self) -> int:
        """Return current checksum."""
        return self._crc_value ^ 0xFFFF  # complement

    @staticmethod
    def compute_checksum(data: bytes, start: int, length: int) -> int:
        """Compute checksum of bytes."""
        fcs = FastFrameCheckSequence16.INIT_FCS_16

        for i in range(start, start + length):
            index = (fcs ^ data[i]) & 0xFF
            fcs = (fcs >> 8) ^ FastFrameCheckSequence16.fast_frame_check_crc_table[
                index
            ]

        return fcs ^ 0xFFFF  # complement
