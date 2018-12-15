import logging
import fastframecheck


class HdlcFrame:
    _buffer = None
    _ffc = None

    def __init__(self):
        self._unescaped_buffer = bytearray()
        self._buffer = bytearray()
        self._ffc = fastframecheck.FastFrameCheckSequence()
        self._escape_next = False
        self._escape_count = 0
        self.is_header_good = None
        self.control_position = None

    def __len__(self):
        return len(self._buffer)

    def append(self, byte):
        self._unescaped_buffer.append(byte)

        if self._escape_next:
            self._escape_next = False
            unescaped = byte ^ 0x20
            self._buffer.append(unescaped)
            self._ffc.update(unescaped)
        else:
            if 0x7d == byte:
                self._escape_next = True
                self._escape_count += 1
            else:
                self._buffer.append(byte)
                self._ffc.update(byte)

        if self.control_position is None:
            self.control_position = self._get_control_field_position()

        if self.control_position is not None:
            if self.is_header_good is None:
                if len(self._buffer) == self.control_position + 3:
                    self.is_header_good = self.is_good

    @property
    def frame_data(self):
        return self._buffer

    @property
    def unescaped_frame_data(self):
        return self._unescaped_buffer

    @property
    def escape_next(self):
        return self._escape_next

    @property
    def is_good(self):
        return self._ffc.is_good

    @property
    def frame_format(self):
        if len(self) >= 2:
            return self._buffer[0] << 8 | self._buffer[1]

    @property
    def frame_format_type(self):
        if self.frame_format is not None:
            return (self.frame_format >> 12) & 0xf

    @property
    def segmentation(self):
        if self.frame_format is not None:
            return ((self.frame_format >> 11) & 0x1) == 0x1

    @property
    def frame_length(self):
        if self.frame_format is not None:
            return self.frame_format & 0x4ff

    @property
    def destination_address(self):
        if len(self) >= 2:
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
        if self.control_position is not None and len(self) >= self.control_position:
            return self._buffer[self.control_position]
        return None

    @property
    def header_check_sequence(self):
        if self.control_position is not None:
            if len(self._buffer) > self.control_position + 3:
                return self._buffer[self.control_position + 2] << 8 | self._buffer[self.control_position + 1]

    @property
    def frame_check_sequence(self):
        """Frame check sequence if complete frame has been read. None or invalid number if not."""
        if self.control_position is not None:
            if len(self._buffer) >= self.control_position + 3:
                return self._buffer[len(self._buffer) - 1] << 8 | self._buffer[len(self._buffer) - 2]

    @property
    def information(self):
        if self.is_good and self.control_position is not None and len(self._buffer) > self.control_position + 3:
            return self._buffer[self.control_position + 3:-2]
        return None

    def _get_address(self, position):
        if len(self) > position:
            adr = bytearray()

            i = position
            while True:
                if i >= len(self):
                    return None

                current = self._buffer[i]
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


class HdlcOctetStuffedFrameReader:
    CONTROL_ESCAPE = b'\x7d'
    FLAG_SEQUENCE = b'\x7e'

    def __init__(self, frame_output, logger=None):
        self._frame_output = frame_output
        self._logger = logger or logging.getLogger(__name__)
        self._buffer = bytearray()
        self._buffer_pos = 0
        self._frame = None

    def read(self, data):
        self._buffer.extend(data)

        if self._frame is None:
            flag_pos = self._buffer.find(self.FLAG_SEQUENCE)
            if flag_pos == -1:
                # flag sequence not found
                self._buffer.clear()
            if flag_pos >= 0:
                if flag_pos > 0:
                    # trim data before flag sequence
                    self._buffer = self._buffer[flag_pos:]
                self._frame = HdlcFrame()
            self._buffer_pos = 0

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
                                    self._frame_output.put_nowait(self._frame)
                                else:
                                    self._logger.warning("Invalid checksum. Discard frame: %s",
                                                         self._frame.unescaped_frame_data.hex())

                                if self._frame._escape_count > 0 and self._frame.is_good:
                                    print("Escaped and good!")

                                if self._frame.segmentation:
                                    print("Is segmentation")

                        self._frame = HdlcFrame()
                        self._buffer = self._buffer[self._buffer_pos:]
                        self._buffer_pos = -1

                else:
                    if current == self.CONTROL_ESCAPE[0]:
                        self._logger.debug("Found control escape")

                    self._frame.append(current)

                self._buffer_pos += 1
