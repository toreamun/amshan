from array import array


class FastFrameCheckSequence:
    """Fast Frame Check Sequence (FCS)"""

    INITFCS16 = 0xffff  # Initial FCS value
    GOODFCS16 = 0xf0b8  # Good final FCS value

    _crc_value = None

    def __init__(self):
        self._crc_value = self.INITFCS16

    @staticmethod
    def _next(crc, byte):
        """Calculate a new fcs CRC given the current CRC value and the new data."""
        crc_index = (crc ^ byte) & 0xff
        return (crc >> 8) ^ fast_frame_check_crc_table[crc_index]

    def update(self, byte):
        """Update the calculated CRC value for the specified input data."""
        self._crc_value = FastFrameCheckSequence._next(self._crc_value, byte)
        return self._crc_value

    @property
    def is_good(self):
        """FCS was designed so that a particular pattern results
   when the FCS operation passes over the complemented FCS.  A good
   frame is indicated by this "good FCS" value"""
        return self.GOODFCS16 == self.checksum

    @property
    def checksum(self):
        return self._crc_value

    @staticmethod
    def compute_crc_table():
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

    @staticmethod
    def compute_checksum(data, start, length):
        fcs = 0xffff
        for i in range(start, start + length):
            index = (fcs ^ data[i]) & 0xff
            fcs = ((fcs >> 8) ^ fast_frame_check_crc_table[index])
        fcs ^= 0xffff
        return fcs


fast_frame_check_crc_table = FastFrameCheckSequence.compute_crc_table()
