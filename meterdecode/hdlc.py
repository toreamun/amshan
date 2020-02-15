import logging
from typing import List

from meterdecode import fastframecheck


class HdlcFrameHeader:

    def __init__(self, frame):
        self._frame = frame
        self._control_position = None
        self._is_header_good = None

    def update(self):
        if self._control_position is None:
            self._control_position = self._get_control_field_position()

        if self._control_position is not None:
            if self._is_header_good is None:
                if len(self._frame.frame_data) == self._control_position + 3:
                    self._is_header_good = self._frame.is_good

    @property
    def frame_format(self):
        if len(self._frame) >= 2:
            return self._frame.frame_data[0] << 8 | self._frame.frame_data[1]
        return None

    @property
    def frame_format_type(self):
        if self.frame_format is not None:
            return (self.frame_format >> 12) & 0xf
        return None

    @property
    def segmentation(self):
        if self.frame_format is not None:
            return ((self.frame_format >> 11) & 0x1) == 0x1
        return None

    @property
    def frame_length(self):
        if self.frame_format is not None:
            return self.frame_format & 0x4ff
        return None

    @property
    def destination_address(self):
        if len(self._frame) >= 2:
            return self._get_address(2)
        return None

    @property
    def source_address(self):
        destination_adr = self.destination_address
        if destination_adr is not None:
            return self._get_address(2 + len(destination_adr))
        return None

    @property
    def control(self):
        if self._control_position is not None and len(self._frame) >= self._control_position:
            return self._frame.frame_data[self._control_position]
        return None

    @property
    def header_check_sequence(self):
        if self._control_position is not None:
            if len(self._frame.frame_data) > self._control_position + 3:
                return self._frame.frame_data[self._control_position + 2] << 8 | self._frame.frame_data[
                    self._control_position + 1]
        return None

    @property
    def information_position(self):
        if self._control_position is not None:
            return self._control_position + 3
        return None

    def _get_address(self, position):
        if len(self._frame) > position:
            adr = bytearray()

            i = position
            while True:
                if i >= len(self._frame):
                    return None

                current = self._frame.frame_data[i]
                adr.append(current)

                if (current & 0x01) == 0x01:
                    return adr

                i += 1

        return None

    def _get_control_field_position(self):
        destination_adr = self.destination_address
        if destination_adr is not None:
            source_adr = self.source_address
            if source_adr is not None:
                return 2 + len(destination_adr) + len(source_adr)
        return None


class HdlcFrame:

    def __init__(self, use_octet_stuffing: bool = False):
        self._use_octet_stuffing = use_octet_stuffing
        self._raw_buffer = bytearray()
        self._buffer = bytearray()
        self._ffc = fastframecheck.FastFrameCheckSequence()
        self._escape_next = False
        self._header = HdlcFrameHeader(self)

    def __len__(self):
        return len(self._buffer)

    def append(self, byte):
        self._raw_buffer.append(byte)

        if self._use_octet_stuffing:
            if self._escape_next:
                self._escape_next = False
                unescaped = byte ^ 0x20
                self._buffer.append(unescaped)
                self._ffc.update(unescaped)
            else:
                if byte == 0x7d:
                    self._escape_next = True
                else:
                    self._buffer.append(byte)
                    self._ffc.update(byte)
        else:
            self._buffer.append(byte)
            self._ffc.update(byte)

        self._header.update()

    @property
    def frame_data(self):
        return self._buffer

    @property
    def unescaped_frame_data(self):
        return self._raw_buffer

    @property
    def escape_next(self):
        return self._escape_next

    @property
    def is_good(self):
        return self._ffc.is_good

    @property
    def header(self):
        return self._header

    @property
    def frame_check_sequence(self):
        """Frame check sequence if complete frame has been read. None or invalid number if not."""
        if self._header.information_position is not None:
            if len(self._buffer) >= self._header.information_position:
                return self._buffer[len(self._buffer) - 1] << 8 | self._buffer[len(self._buffer) - 2]
        return None

    @property
    def information(self):
        if self.is_good:
            info_position = self._header.information_position
            if info_position is not None and len(self._buffer) > info_position:
                return self._buffer[info_position:-2]
        return None


class HdlcOctetStuffedFrameReader:
    CONTROL_ESCAPE = b'\x7d'
    FLAG_SEQUENCE = b'\x7e'

    def __init__(self, use_octet_stuffing: bool = False, logger=None):
        self._use_octet_stuffing = use_octet_stuffing
        self._logger = logger or logging.getLogger(__name__)
        self._buffer = bytearray()
        self._buffer_pos = 0
        self._frame = None

    def read(self, data: bytes) -> List[HdlcFrame]:
        frames_received = []

        self._buffer.extend(data)

        if self._frame is None:
            self._trim_buffer()

        if len(self._buffer) > 0:
            while self._buffer_pos < len(self._buffer):
                current = self._buffer[self._buffer_pos]

                if current == self.FLAG_SEQUENCE[0]:

                    if len(self._frame) == 0:
                        self._logger.debug("Found flag sequence -> start of frame")
                    else:
                        self._logger.debug("Found flag sequence -> end of frame")

                        if len(self._frame) < 4:
                            # Frames which are too short (less than 4 octets)
                            # are silently discarded, and not counted as a FCS error.
                            self._logger.info("Too short frame (%d bytes). Discard frame: %s",
                                              len(self._frame), self._frame.unescaped_frame_data.hex())
                        else:
                            if self._frame.escape_next:
                                # Frames which end with a Control Escape octet
                                # followed immediately by a closing Flag Sequence,
                                # are silently discarded, and not counted as a FCS error.
                                self._logger.info("Abort sequence. Discard frame: %s",
                                                  self._frame.unescaped_frame_data.hex())
                            else:
                                if self._frame.is_good:
                                    self._logger.info("Frame of length %d successfully received", len(self._frame))
                                else:
                                    self._logger.warning("Frame of length %d received with invalid checksum",
                                                         len(self._frame))

                                frames_received.append(self._frame)

                                if self._frame.header.segmentation:
                                    print("Is segmentation")

                        self._frame = HdlcFrame(self._use_octet_stuffing)
                        self._buffer = self._buffer[self._buffer_pos:]
                        self._buffer_pos = -1

                else:
                    if self._use_octet_stuffing and current == self.CONTROL_ESCAPE[0]:
                        self._logger.debug("Found control escape")

                    self._frame.append(current)

                self._buffer_pos += 1

        return frames_received

    def _trim_buffer(self):
        flag_pos = self._buffer.find(self.FLAG_SEQUENCE)
        if flag_pos == -1:
            # flag sequence not found
            self._buffer.clear()
        if flag_pos >= 0:
            if flag_pos > 0:
                # trim data before flag sequence
                self._buffer = self._buffer[flag_pos:]
            self._frame = HdlcFrame(self._use_octet_stuffing)
        self._buffer_pos = 0
