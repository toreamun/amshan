from array import array

"""
16-bit Fast Frame Check Sequence (FCS) Implementation derived from https://tools.ietf.org/rfc/rfc1662#appendix-C
"""


def compute_fcs_16_crc_table():
    """Generate a FCS-16 table"""
    polynomial = 0x8408
    crc_table = array('H')
    for byte in range(256):
        crc = 0
        for bit in range(8):
            if (byte ^ crc) & 1:
                crc = (crc >> 1) ^ polynomial
            else:
                crc >>= 1
            byte >>= 1
        crc_table.append(crc)
    return crc_table


class FastFrameCheckSequence:
    """16 bit Fast Frame Check Sequence (FCS)"""

    INIT_FCS_16 = 0xffff  # Initial FCS value
    GOOD_FCS_16 = 0xf0b8  # Good final FCS value

    _fast_frame_check_crc_table = compute_fcs_16_crc_table()

    def __init__(self):
        self._crc_value = self.INIT_FCS_16

    @staticmethod
    def _next(crc, byte):
        """Calculate a new fcs CRC given the current CRC value and the new data."""
        crc_index = (crc ^ byte) & 0xff
        return (crc >> 8) ^ FastFrameCheckSequence._fast_frame_check_crc_table[crc_index]

    def update(self, byte):
        """Update the calculated CRC value for the specified input data."""
        self._crc_value = FastFrameCheckSequence._next(self._crc_value, byte)
        return self._crc_value

    @property
    def is_good(self):
        """
        FCS was designed so that a particular pattern results
        when the FCS operation passes over the complemented FCS.  A good
        frame is indicated by this "good FCS" value
        """
        return self.GOOD_FCS_16 == self._crc_value

    @property
    def checksum(self):
        return self._crc_value ^ 0xffff

    @staticmethod
    def compute_checksum(data, start, length):
        fcs = FastFrameCheckSequence.INIT_FCS_16

        for i in range(start, start + length):
            index = (fcs ^ data[i]) & 0xff
            fcs = ((fcs >> 8) ^ FastFrameCheckSequence._fast_frame_check_crc_table[index])

        return fcs ^ 0xffff  # complement
