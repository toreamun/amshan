"""
Use this module to read HDLC frames
"""
import logging
from typing import List, Optional

from smartmeterdecode import fastframecheck


class HdlcFrameHeader:
    """The start (header) of an HdlcFrame."""

    def __init__(self, frame):
        """The header constructor used by parent frame"""
        self._frame = frame
        self._control_position = None
        self._is_header_good = None

    def update(self):
        """Update fields when more frame data has been read. Used by parent HdlcFrame."""
        if self._control_position is None and len(self._frame) > 3:
            self._control_position = self._get_control_field_position()

        if self._control_position is not None:
            if self._is_header_good is None:
                if len(self._frame.frame_data) == self._control_position + 3:
                    self._is_header_good = self._frame.is_good_ffc

    @property
    def frame_format(self) -> Optional[int]:
        """The value of frame format if the value has been read."""

        # The length of the frame format field is two bytes. It consists of three sub-fields referred to as the Format
        # type sub-field (4 bit), the Segmentation bit (S, 1 bit) and the frame length sub-field (11 bit).
        if len(self._frame) >= 2:
            return self._frame.frame_data[0] << 8 | self._frame.frame_data[1]
        return None

    @property
    def frame_format_type(self) -> Optional[int]:
        """The value of frame format type sub-field when frame format has been read."""
        if self.frame_format is not None:
            return (self.frame_format >> 12) & 0b1111
        return None

    @property
    def segmentation(self) -> Optional[bool]:
        """The value of frame format Segmentation flag when frame format has been read."""
        if self.frame_format is not None:
            return ((self.frame_format >> 11) & 0x1) == 0x1
        return None

    @property
    def frame_length(self) -> Optional[int]:
        """
        The value of frame format length sub-field when frame format has been read.
        The value of the frame length subfield is the count of octets in the frame
        excluding the opening and closing frame flag sequences.
        """
        if self.frame_format is not None:
            return self.frame_format & 0b11111111111
        return None

    @property
    def destination_address(self) -> Optional[bytearray]:
        """
        The value of destination address when the field has been read.
        Depending on the direction of the data transfer, both the client and the server addresses can
        be destination or source addresses.
        The client address shall always be expressed on one byte.
        """
        if len(self._frame) >= 2:
            return self._get_address(2)
        return None

    @property
    def source_address(self) -> Optional[bytearray]:
        """
        The value of source address when the field has been read.
        Depending on the direction of the data transfer, both the client and the server addresses can
        be destination or source addresses.
        The client address shall always be expressed on one byte.
        """
        destination_adr = self.destination_address
        if destination_adr is not None:
            return self._get_address(2 + len(destination_adr))
        return None

    @property
    def control(self) -> Optional[int]:
        """
        The value of control field when the field has been read.
        It indicates the type of commands or responses,
        and contains sequence numbers, where appropriate (frames I, RR and RNR).
        """
        is_available = (
            self._control_position is not None
            and len(self._frame) > self._control_position
        )
        if is_available:
            return self._frame.frame_data[self._control_position]
        return None

    @property
    def header_check_sequence(self) -> Optional[int]:
        """
        Header check sequence (HCS) field when the field has been read.
        This check sequence is applied to only the header,
        i.e., the bits between the opening flag sequence and the header check sequence.
        """
        is_available = (
            self._control_position is not None
            and len(self._frame) > self._control_position + 2
        )
        if is_available:
            return (
                self._frame.frame_data[self._control_position + 1] << 8
                | self._frame.frame_data[self._control_position + 2]
            )
        return None

    @property
    def information_position(self) -> Optional[int]:
        """
        Information field position when the field position is known and is available.
        Frames that do not have an information field or have an empty information field,
        e.g., as with some supervisory frames, do not contain an HCS and FCS, only an FCS.
        """
        if self._control_position is not None:
            return self._control_position + 3
        return None

    def _get_address(self, position) -> Optional[bytearray]:
        """Get variable length address from position."""

        # As specified in ISO/IEC 13239:2002, 4.7.1, The address field range can be extended by reserving the first
        # transmitted bit (low-order) of each address octet which would then be set to binary zero to indicate that
        # the following octet is an extension of the address field. The format of the extended octet(s) shall be the
        # same as that of the first octet. Thus, the address field may be recursively extended. The last octet of an
        # address field is indicted by setting the low-order bit to binary one.

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
    """
    Use this class to read HDLC frames. Call append for each byte.
    is_good is true when checksum is ok. This can be the case both when header is read
    and when done reading information.
    """

    def __init__(self):
        """Construct HdlcFrame."""
        self._frame_data = bytearray()
        self._ffc = fastframecheck.FastFrameCheckSequence16()
        self._escape_next = False
        self._header = HdlcFrameHeader(self)

    # Frame length is specified with 11 bit.
    MAX_FRAME_LENGTH: int = 0b11111111111

    def __len__(self):
        """
        Length of currently parsed bytes.
        Note that expected complete frame length is found in header when header has been read.
        """
        return len(self._frame_data)

    def append(self, byte) -> None:
        """Append byte to frame."""
        self._frame_data.append(byte)
        self._ffc.update(byte)
        self._header.update()

    @property
    def frame_data(self) -> bytearray:
        """
        Frame data bytes. Data has been unescaped when the reader uses octet frame stuffing (see constructor).
        """
        return self._frame_data

    @property
    def is_good_ffc(self) -> bool:
        """
        Current Fast Frame Check calculation state is good when true.
        Can be true for both end of header and body.
        """
        return self._ffc.is_good

    @property
    def is_expected_length(self) -> bool:
        """True when current length is the same as length from header."""
        return self._header.frame_length == len(self)

    @property
    def header(self) -> HdlcFrameHeader:
        """Frame header."""
        return self._header

    @property
    def frame_check_sequence(self) -> Optional[int]:
        """Frame check sequence if complete frame has been read. None or invalid number if not."""
        if self._header.information_position is not None:
            if len(self._frame_data) >= self._header.information_position:
                return (
                    self._frame_data[len(self._frame_data) - 2] << 8
                    | self._frame_data[len(self._frame_data) - 1]
                )
        return None

    @property
    def information(self) -> Optional[bytearray]:
        """Information field when the field has been read and is available."""
        info_position = self._header.information_position
        if info_position is not None and len(self._frame_data) > info_position:
            return self._frame_data[info_position:-2]
        return None


class HdlcFrameReader:
    """Use this class to HDLC-frames as stream of bytes."""

    # The Control Escape octet is defined as binary 01111101 (hexadecimal 0x7d)
    CONTROL_ESCAPE = 0x7D

    # The Flag Sequence indicates the beginning or end of a frame.
    # The octet stream is examined on an octet-by-octet basis for the value 01111110 (hexadecimal 0x7e).
    FLAG_SEQUENCE = 0x7E

    def __init__(
        self, use_octet_stuffing: bool = False, use_abort_sequence=False, logger=None
    ) -> None:
        """
        Construct HHdlcFrameReader.
        :param use_octet_stuffing: true to use octet stuffing (0x7D as escape octet)
        """
        self._use_octet_stuffing = use_octet_stuffing
        self._use_abort_sequence = use_abort_sequence
        self._unescape_next = False
        self._logger = logger or logging.getLogger(__name__)
        self._buffer = ReaderBuffer()
        self._raw_frame_data = bytearray()
        self._frame: Optional[HdlcFrame] = None

    @property
    def unescape_next(self) -> bool:
        """True if octet stuffing is used and next octet is escaped and must be unescaped."""
        return self._unescape_next

    @property
    def is_in_hunt_mode(self) -> bool:
        """True when reader is hunting for start of frame."""
        return self._frame is None

    def read(self, data_chunk: bytes) -> List:
        """
        Call this function to read chunks of bytes.
        :param data_chunk: next bytes to parsed.
        :return: frame when a frame is complete (both with correct and incorrect checksum).
        """
        frames_received: List[HdlcFrame] = []

        self._buffer.extend(data_chunk)

        if self.is_in_hunt_mode:
            self._buffer.trim_buffer_to_flag_or_end()

        while self._buffer.is_available:
            frame_complete = self._read_next()
            if frame_complete:
                self._logger.info(
                    "Frame of %s length %d received with %s checksum.",
                    "expected" if self._frame.is_expected_length else "unexpected",
                    len(self._frame),
                    "good" if self._frame.is_good_ffc else "bad",
                )
                frames_received.append(self._frame)
                self._start_frame()
                self._buffer.trim_buffer_to_current_position()

        return frames_received

    def _read_next(self) -> bool:
        frame_complete = False

        current = self._buffer.pop()
        is_flag = current == self.FLAG_SEQUENCE
        if is_flag:
            frame_complete = self._handle_flag_sequence()
        elif not self.is_in_hunt_mode:
            self._append_to_frame(current)
            if len(self._frame) > HdlcFrame.MAX_FRAME_LENGTH:
                self._logger.warning(
                    "Max frame length reached. Discard frame: %s",
                    self._raw_frame_data.hex(),
                )
                self._goto_hunt_mode()
                frame_complete = False

        return frame_complete

    def _handle_flag_sequence(self):
        frame_complete = False

        if self.is_in_hunt_mode:
            self._logger.debug("Found flag sequence in frame hunt mode")
            self._start_frame()

        elif len(self._frame) == 0:
            # Found new flag sequence. Two is normal ( end + start), one is allowed, and many possible if time fill.
            pass

        elif self._frame.header.header_check_sequence is None:
            # Frames which are too short are silently discarded, and not counted as a FCS error.
            self._logger.info(
                "Found flag sequence. Too short frame (%d bytes). Discard frame: %s",
                len(self._frame),
                self._raw_frame_data.hex(),
            )
            self._goto_hunt_mode()

        # check if previous octet was Control Escape if abort sequence is activated
        elif (
            self._use_abort_sequence
            and len(self._raw_frame_data) > 1
            and self._raw_frame_data[-1:][0] == self.CONTROL_ESCAPE
        ):
            # Frames which end with a Control Escape octet
            # followed immediately by a closing Flag Sequence,
            # are silently discarded, and not counted as a FCS error.
            self._logger.info(
                "Abort sequence. Discard frame: %s", self._raw_frame_data.hex()
            )
            self._goto_hunt_mode()

        elif self._use_octet_stuffing:
            # Control Escape is never in content when using octet stuffing
            frame_complete = True

        elif self._frame.is_expected_length:
            frame_complete = True

        else:
            self._append_to_frame(self.FLAG_SEQUENCE)

        return frame_complete

    def _append_to_frame(self, current):
        self._raw_frame_data.append(current)
        if self._use_octet_stuffing:
            if self._unescape_next:
                self._unescape_next = False
                unescaped = current ^ 0x20
                self._frame.append(unescaped)
            else:
                if current == HdlcFrameReader.CONTROL_ESCAPE:
                    self._unescape_next = True
                else:
                    self._frame.append(current)
        else:
            self._frame.append(current)

    def _start_frame(self):
        self._frame = HdlcFrame()
        self._raw_frame_data.clear()

    def _goto_hunt_mode(self):
        self._frame = None
        self._buffer.trim_buffer_to_flag_or_end()


class ReaderBuffer:
    """Buffer class used by HdlcFrameReader"""

    def __init__(self):
        self._buffer = bytearray()
        self._buffer_pos = 0

    @property
    def is_available(self) -> bool:
        return len(self._buffer) > self._buffer_pos

    def pop(self):
        if self.is_available:
            byte = self._buffer[self._buffer_pos]
            self._buffer_pos += 1
            return byte
        return None

    def extend(self, data_chunk: bytes):
        self._buffer.extend(data_chunk)

    def trim_buffer_to_current_position(self):
        self._buffer = self._buffer[self._buffer_pos :]
        self._buffer_pos = 0

    def trim_buffer_to_flag_or_end(self):
        self.trim_buffer_to_current_position()
        flag_pos = self._buffer.find(HdlcFrameReader.FLAG_SEQUENCE)
        if flag_pos == -1:
            # flag sequence not found
            self._buffer.clear()
        if flag_pos > 0:
            # trim data before flag sequence
            self._buffer = self._buffer[flag_pos:]
        self._buffer_pos = 0