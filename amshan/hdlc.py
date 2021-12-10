"""Use this module to read HDLC frames."""
import logging
from typing import List, Optional, cast

from amshan import fastframecheck

_LOGGER = logging.getLogger(__name__)


class HdlcFrameHeader:
    """The start (header) of an HdlcFrame."""

    def __init__(self, frame: "HdlcFrame") -> None:
        """
        Initialize header.

        Used by parent frame.
        """
        self._frame: HdlcFrame = frame
        self._control_position: Optional[int] = None
        self._is_header_good: Optional[bool] = None

    def update(self) -> None:
        """Update fields when more frame data has been read. Used by parent HdlcFrame."""
        if self._control_position is None and len(self._frame) > 3:
            self._control_position = self._get_control_field_position()

        if self._control_position is not None:
            if self._is_header_good is None:
                if len(self._frame) == self._control_position + 3:
                    self._is_header_good = self._frame.is_good_ffc

    @property
    def frame_format(self) -> Optional[int]:
        """Return the value of frame format if the value has been read."""
        # The length of the frame format field is two bytes. It consists of three sub-fields referred to as the Format
        # type sub-field (4 bit), the Segmentation bit (S, 1 bit) and the frame length sub-field (11 bit).
        if len(self._frame) >= 2:
            return self._frame.frame_data[0] << 8 | self._frame.frame_data[1]
        return None

    @property
    def frame_format_type(self) -> Optional[int]:
        """Return the value of frame format type sub-field when frame format has been read."""
        if self.frame_format is not None:
            return (self.frame_format >> 12) & 0b1111
        return None

    @property
    def segmentation(self) -> Optional[bool]:
        """Return the value of frame format Segmentation flag when frame format has been read."""
        if self.frame_format is not None:
            return ((self.frame_format >> 11) & 0x1) == 0x1
        return None

    @property
    def frame_length(self) -> Optional[int]:
        """
        Return the value of frame format length sub-field when frame format has been read.

        The value of the frame length subfield is the count of octets in the frame
        excluding the opening and closing frame flag sequences.
        """
        if self.frame_format is not None:
            return self.frame_format & 0b11111111111
        return None

    @property
    def destination_address(self) -> Optional[bytes]:
        """
        Return the value of destination address when the field has been read.

        Depending on the direction of the data transfer, both the client and the server addresses can
        be destination or source addresses.

        The client address shall always be expressed on one byte.
        """
        if len(self._frame) >= 2:
            return self._get_address(2)
        return None

    @property
    def source_address(self) -> Optional[bytes]:
        """
        Return the value of source address when the field has been read.

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
        Return the value of control field when the field has been read.

        It indicates the type of commands or responses,
        and contains sequence numbers, where appropriate (frames I, RR and RNR).
        """
        is_available = (
            self._control_position is not None
            and len(self._frame) > self._control_position
        )
        if is_available:
            return self._frame.frame_data[cast(int, self._control_position)]
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
                self._frame.frame_data[cast(int, self._control_position) + 1] << 8
                | self._frame.frame_data[cast(int, self._control_position) + 2]
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

    def _get_address(self, position: int) -> Optional[bytes]:
        """Get variable length address from position."""
        # As specified in ISO/IEC 13239:2002, 4.7.1, The address field range can be extended by reserving the first
        # transmitted bit (low-order) of each address octet which would then be set to binary zero to indicate that
        # the following octet is an extension of the address field. The format of the extended octet(s) shall be the
        # same as that of the first octet. Thus, the address field may be recursively extended. The last octet of an
        # address field is indicted by setting the low-order bit to binary one.

        if len(self._frame) > position:
            adr = bytearray()

            i = position
            frame_data = self._frame.frame_data
            while True:
                if i >= len(self._frame):
                    return None

                current = frame_data[i]
                adr.append(current)

                if (current & 0x01) == 0x01:
                    return bytes(adr)

                i += 1

        return None

    def _get_control_field_position(self) -> Optional[int]:
        destination_adr = self.destination_address
        if destination_adr is not None:
            source_adr = self.source_address
            if source_adr is not None:
                return 2 + len(destination_adr) + len(source_adr)
        return None


class HdlcFrame:
    """
    Use this class to read HDLC frames by calling append for each byte.

    is_good is true when checksum is ok. This can be the case both when header is read
    and when done reading information.
    """

    def __init__(self) -> None:
        """Construct HdlcFrame."""
        self._frame_data = bytearray()
        self._ffc = fastframecheck.FastFrameCheckSequence16()
        self._escape_next = False
        self._header = HdlcFrameHeader(self)

    # Frame length is specified with 11 bit.
    MAX_FRAME_LENGTH: int = 0b11111111111

    def __len__(self) -> int:
        """
        Length of currently parsed bytes.

        Note that expected complete frame length is found in header when header has been read.
        """
        return len(self._frame_data)

    def append(self, byte: int) -> None:
        """Append byte to frame."""
        self._frame_data.append(byte)
        self._ffc.update(byte)
        self._header.update()

    @property
    def frame_data(self) -> bytes:
        """
        Return frame data bytes.

        Data has been unescaped when the reader uses octet frame stuffing (see constructor).
        """
        return bytes(self._frame_data)

    @property
    def is_good_ffc(self) -> bool:
        """
        Return Current Fast Frame Check calculation state.

        Can be true for both end of header and body.
        """
        return self._ffc.is_good

    @property
    def is_expected_length(self) -> bool:
        """Return True when current length is the same as length from header."""
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
    def information(self) -> Optional[bytes]:
        """Information field when the field has been read and is available."""
        info_position = self._header.information_position
        if info_position is not None and len(self._frame_data) > info_position:
            return bytes(self._frame_data[info_position:-2])
        return None


class HdlcFrameReader:
    """Use this class to HDLC-frames as stream of bytes."""

    # The Control Escape octet is defined as binary 01111101 (hexadecimal 0x7d)
    CONTROL_ESCAPE: int = 0x7D

    # The Flag Sequence indicates the beginning or end of a frame.
    # The octet stream is examined on an octet-by-octet basis for the value 01111110 (hexadecimal 0x7e).
    FLAG_SEQUENCE: int = 0x7E

    def __init__(
        self, use_octet_stuffing: bool = False, use_abort_sequence: bool = False
    ) -> None:
        """
        Construct HHdlcFrameReader.

        :param use_octet_stuffing: true to use octet stuffing (0x7D as escape octet)
        """
        self._use_octet_stuffing = use_octet_stuffing
        self._use_abort_sequence = use_abort_sequence
        self._unescape_next = False
        self._buffer = _ReaderBuffer()
        self._raw_frame_data = bytearray()
        self._frame: Optional[HdlcFrame] = None

    @property
    def unescape_next(self) -> bool:
        """Return True if octet stuffing is used and next octet is escaped and must be unescaped."""
        return self._unescape_next

    @property
    def is_in_hunt_mode(self) -> bool:
        """Return True when reader is hunting for start of frame."""
        return self._frame is None

    def read(self, data_chunk: bytes) -> List[HdlcFrame]:
        """
        Call this function to read chunks of bytes.

        :param data_chunk: next bytes to parsed.
        :return: frame when a frame is complete (both with correct and incorrect checksum).
        """
        frames_received: List[HdlcFrame] = []

        self._buffer.extend(data_chunk)

        if self._frame is None:  # in hunt mode
            self._buffer.trim_buffer_to_flag_or_end()

        while self._buffer.is_available:
            frame_complete = self._read_next()
            if frame_complete:
                _LOGGER.debug(
                    "Frame of %s length %d received with %s checksum.",
                    "expected"
                    if cast(HdlcFrame, self._frame).is_expected_length
                    else "unexpected",
                    len(cast(HdlcFrame, self._frame)),
                    "good" if cast(HdlcFrame, self._frame).is_good_ffc else "bad",
                )
                frames_received.append(cast(HdlcFrame, self._frame))
                self._start_frame()
                self._buffer.trim_buffer_to_current_position()

        return frames_received

    def _read_next(self) -> bool:
        frame_complete = False

        current = self._buffer.pop()
        is_flag = current == self.FLAG_SEQUENCE
        if is_flag:
            frame_complete = self._handle_flag_sequence()
        elif self._frame is not None:  # not in hunt mode
            self._append_to_frame(current)
            if len(self._frame) > HdlcFrame.MAX_FRAME_LENGTH:
                _LOGGER.debug(
                    "Max frame length reached. Discard frame: %s",
                    self._raw_frame_data.hex(),
                )
                self._goto_hunt_mode()
                frame_complete = False

        return frame_complete

    def _handle_flag_sequence(self) -> bool:
        frame_complete = False

        if self._frame is None:
            _LOGGER.debug("Found flag sequence in frame hunt mode")
            self._start_frame()

        elif len(self._frame) == 0:
            # Found new flag sequence. Two is normal ( end + start), one is allowed, and many possible if time fill.
            pass

        elif self._frame.header.header_check_sequence is None:
            # Frames which are too short are silently discarded, and not counted as a FCS error.
            _LOGGER.debug(
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
            _LOGGER.debug(
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

    def _append_to_frame(self, current: int) -> None:
        assert self._frame is not None
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

    def _start_frame(self) -> None:
        self._frame = HdlcFrame()
        self._raw_frame_data.clear()

    def _goto_hunt_mode(self) -> None:
        self._frame = None
        self._buffer.trim_buffer_to_flag_or_end()


class _ReaderBuffer:
    """Buffer class used by HdlcFrameReader."""

    def __init__(self) -> None:
        self._buffer = bytearray()
        self._buffer_pos = 0

    @property
    def is_available(self) -> bool:
        """Byte(s) are available."""
        return len(self._buffer) > self._buffer_pos

    def pop(self) -> int:
        """Pop one byte from buffer."""
        byte = self._buffer[self._buffer_pos]
        self._buffer_pos += 1
        return byte

    def extend(self, data_chunk: bytes) -> None:
        """Add bytes to buffer."""
        self._buffer.extend(data_chunk)

    def trim_buffer_to_current_position(self) -> None:
        """Trim buffer to current position."""
        self._buffer = self._buffer[self._buffer_pos :]
        self._buffer_pos = 0

    def trim_buffer_to_flag_or_end(self) -> None:
        """Trim buffer to flag sequence or end of buffer."""
        self.trim_buffer_to_current_position()
        flag_pos = self._buffer.find(HdlcFrameReader.FLAG_SEQUENCE)
        if flag_pos == -1:
            # flag sequence not found
            self._buffer.clear()
        if flag_pos > 0:
            # trim data before flag sequence
            self._buffer = self._buffer[flag_pos:]
        self._buffer_pos = 0
