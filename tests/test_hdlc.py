"""HDLC tests."""

# pylint: disable = no-self-use
from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st

from han import hdlc
from tests import frames

FLAG_SEQUENCE = "7e"
CONTROL_ESCAPE = "7d"

FRAME_EMPTY_INFO = "a00801020110378d"
FRAME_SHORT_INFO = "a00C0102011027a00201e7de"
FRAME_WITH_ESCAPE_CHARACTER_IN_INFO = "a02a410883130413e6e7000f40000000000101020309060100010700ff060000067d02020f00161b1c05"
FRAME_WITH_FLAG_SEQUENCE_CHARACTER_IN_INFO = (
    "a027010201105a87e6e7000f40000000090c07e4020f06011922ff8000000201060000157eea5e"
)
STUFFED_FRAME_SHORT_INFO = "a00d0102011063ab7d5e7d5d7d23932D"


class TestHdlcFrameReader:
    """Test HdlcFrameReader."""

    def test_frame_with_escape_character(self):
        """Test fram with escape character."""
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE + FRAME_WITH_ESCAPE_CHARACTER_IN_INFO + FLAG_SEQUENCE
        )

        frame_reader = hdlc.HdlcFrameReader(False)
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 1
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert (
            frames[0].payload
            == bytes.fromhex(FRAME_WITH_ESCAPE_CHARACTER_IN_INFO)[8:-2]
        )

    def test_frame_with_control_character_in_content(self):
        """Test frame with control character in content."""
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE + FRAME_WITH_FLAG_SEQUENCE_CHARACTER_IN_INFO + FLAG_SEQUENCE
        )

        frame_reader = hdlc.HdlcFrameReader(False)
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 1
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert (
            frames[0].payload
            == bytes.fromhex(FRAME_WITH_FLAG_SEQUENCE_CHARACTER_IN_INFO)[8:-2]
        )

    @pytest.mark.parametrize(
        "data_feed",
        [
            bytes.fromhex("c3" + FLAG_SEQUENCE + FRAME_SHORT_INFO + FLAG_SEQUENCE),
            bytes.fromhex(
                "0600001fc7cec3" + FLAG_SEQUENCE + FRAME_SHORT_INFO + FLAG_SEQUENCE
            ),
        ],
    )
    def test_start_read_in_frame(self, data_feed):
        """Test start reading in middle of frame."""
        frame_reader = hdlc.HdlcFrameReader(False)
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 1
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].payload == bytes.fromhex(FRAME_SHORT_INFO)[8:-2]

    def test_empty_info_frame(self):
        """Test read empty frame."""
        data_feed = bytes.fromhex(FLAG_SEQUENCE + FRAME_EMPTY_INFO + FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 1
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].header.header_check_sequence is not None
        assert frames[0].payload is None

    def test_too_short_frame_is_discarded(self):
        """Test that too short frame is discarded."""
        data_feed = bytes.fromhex(FLAG_SEQUENCE + "a0080102011037" + FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 0

    def test_abort_sequence(self):
        """Control escape followed by flag aborts the frame when octet stuffing is used."""
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE + FRAME_SHORT_INFO + CONTROL_ESCAPE + FLAG_SEQUENCE
        )

        frame_reader = hdlc.HdlcFrameReader(
            use_octet_stuffing=True, use_abort_sequence=True
        )
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 0

    def test_single_flag_sequences_between_frames(self):
        """Test single flag sequnce between frames."""
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE
            + FRAME_SHORT_INFO
            + FLAG_SEQUENCE
            + FRAME_EMPTY_INFO
            + FLAG_SEQUENCE
        )

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 2
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].payload == bytes.fromhex(FRAME_SHORT_INFO)[8:-2]
        assert frames[1].is_good_ffc
        assert frames[1].is_expected_length
        assert frames[1].payload is None

    def test_two_flag_sequences_between_frames(self):
        """Test double flag seqeuncene between frames."""
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE
            + FRAME_SHORT_INFO
            + FLAG_SEQUENCE
            + FLAG_SEQUENCE
            + FRAME_EMPTY_INFO
            + FLAG_SEQUENCE
        )

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 2
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].payload == bytes.fromhex(FRAME_SHORT_INFO)[8:-2]
        assert frames[1].is_good_ffc
        assert frames[1].is_expected_length
        assert frames[1].payload is None

    def test_many_flag_sequences_between_frames(self):
        """Test many flag seqeunces between frames."""
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE
            + FRAME_SHORT_INFO
            + FLAG_SEQUENCE
            + FLAG_SEQUENCE
            + FLAG_SEQUENCE
            + FLAG_SEQUENCE
            + FLAG_SEQUENCE
            + FLAG_SEQUENCE
            + FRAME_EMPTY_INFO
            + FLAG_SEQUENCE
        )

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 2
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].payload == bytes.fromhex(FRAME_SHORT_INFO)[8:-2]
        assert frames[1].is_good_ffc
        assert frames[1].is_expected_length
        assert frames[1].payload is None

    def test_stuffed_frame_short_info(self):
        """Test stuffed frame."""
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE + STUFFED_FRAME_SHORT_INFO + FLAG_SEQUENCE
        )

        frame_reader = hdlc.HdlcFrameReader(True)
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 1
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].header.header_check_sequence is not None
        assert frames[0].payload == bytes.fromhex("7e7d03")

    def test_too_long_frame_is_discarded(self):
        """Test too long frame is discarded."""
        data_feed = bytes.fromhex(FLAG_SEQUENCE + FRAME_SHORT_INFO) + bytearray(
            hdlc.HdlcFrame.MAX_FRAME_LENGTH
        )

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 0


class TestHdlcFrameHeader:
    """Test HdlcFrameHeader."""

    def test_empty_frame(self):
        """Test empty frame."""
        frame = hdlc.HdlcFrame()

        assert frame.header is not None

        assert frame.header.frame_format is None
        assert frame.header.frame_format_type is None
        assert frame.header.segmentation is None
        assert frame.header.frame_length is None
        assert frame.header.destination_address is None
        assert frame.header.source_address is None
        assert frame.header.information_position is None
        assert frame.header.control is None
        assert frame.header.header_check_sequence is None

    def test_read_byte(self):
        """Test read byte."""
        frame = hdlc.HdlcFrame()

        fragment = bytes.fromhex(FRAME_SHORT_INFO)[:1]
        for byte in fragment:
            frame.append(byte)

        assert frame.header is not None

        assert frame.header.frame_format is None
        assert frame.header.frame_format_type is None
        assert frame.header.segmentation is None
        assert frame.header.frame_length is None
        assert frame.header.destination_address is None
        assert frame.header.source_address is None
        assert frame.header.information_position is None
        assert frame.header.control is None
        assert frame.header.header_check_sequence is None

    def test_read_including_frame_format(self):
        """Test read past frame format."""
        frame = hdlc.HdlcFrame()

        fragment = bytes.fromhex(FRAME_SHORT_INFO)[:2]
        for byte in fragment:
            frame.append(byte)

        assert frame.header is not None

        assert frame.header.frame_format is not None
        assert (
            frame.header.frame_format_type
            == (int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0xF000) >> 12
        )
        assert (
            frame.header.segmentation
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x800
        )
        assert (
            frame.header.frame_length
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x7FF
        )

        assert frame.header.destination_address is None
        assert frame.header.source_address is None
        assert frame.header.information_position is None
        assert frame.header.control is None
        assert frame.header.header_check_sequence is None

    def test_read_including_destination_address(self):
        """Test read past destination address."""
        frame = hdlc.HdlcFrame()

        fragment = bytes.fromhex(FRAME_SHORT_INFO)[:3]
        for byte in fragment:
            frame.append(byte)

        assert frame.header is not None

        assert frame.header.frame_format is not None
        assert (
            frame.header.frame_format_type
            == (int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0xF000) >> 12
        )
        assert (
            frame.header.segmentation
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x800
        )
        assert (
            frame.header.frame_length
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x7FF
        )

        assert frame.header.destination_address == bytes.fromhex(
            FRAME_SHORT_INFO[2 * 2 : 3 * 2]
        )
        assert frame.header.source_address is None
        assert frame.header.information_position is None
        assert frame.header.control is None
        assert frame.header.header_check_sequence is None

    def test_read_including_halve_source_address(self):
        """Test read past halve source address."""
        frame = hdlc.HdlcFrame()

        fragment = bytes.fromhex(FRAME_SHORT_INFO)[:4]
        for byte in fragment:
            frame.append(byte)

        assert frame.header is not None

        assert frame.header.frame_format is not None
        assert (
            frame.header.frame_format_type
            == (int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0xF000) >> 12
        )
        assert (
            frame.header.segmentation
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x800
        )
        assert (
            frame.header.frame_length
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x7FF
        )

        assert frame.header.destination_address == bytes.fromhex(
            FRAME_SHORT_INFO[2 * 2 : 3 * 2]
        )
        assert frame.header.source_address is None
        assert frame.header.information_position is None
        assert frame.header.control is None
        assert frame.header.header_check_sequence is None

    def test_read_including_source_address(self):
        """Test read past source address."""
        frame = hdlc.HdlcFrame()

        fragment = bytes.fromhex(FRAME_SHORT_INFO)[:5]
        for byte in fragment:
            frame.append(byte)

        assert frame.header is not None

        assert frame.header.frame_format is not None
        assert (
            frame.header.frame_format_type
            == (int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0xF000) >> 12
        )
        assert (
            frame.header.segmentation
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x800
        )
        assert (
            frame.header.frame_length
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x7FF
        )

        assert frame.header.destination_address == bytes.fromhex(
            FRAME_SHORT_INFO[2 * 2 : 3 * 2]
        )
        assert frame.header.source_address == bytes.fromhex(
            FRAME_SHORT_INFO[3 * 2 : 5 * 2]
        )
        assert frame.header.information_position == 8
        assert frame.header.control is None
        assert frame.header.header_check_sequence is None

    def test_read_including_control(self):
        """Test read past control."""
        frame = hdlc.HdlcFrame()

        fragment = bytes.fromhex(FRAME_SHORT_INFO)[:6]
        for byte in fragment:
            frame.append(byte)

        assert frame.header is not None

        assert frame.header.frame_format is not None
        assert (
            frame.header.frame_format_type
            == (int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0xF000) >> 12
        )
        assert (
            frame.header.segmentation
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x800
        )
        assert (
            frame.header.frame_length
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x7FF
        )

        assert frame.header.destination_address == bytes.fromhex(
            FRAME_SHORT_INFO[2 * 2 : 3 * 2]
        )
        assert frame.header.source_address == bytes.fromhex(
            FRAME_SHORT_INFO[3 * 2 : 5 * 2]
        )
        assert frame.header.information_position == 8
        assert frame.header.control == 16
        assert frame.header.header_check_sequence is None

    def test_read_halve_header_check_sequence(self):
        """Test read past halve header check sequence."""
        frame = hdlc.HdlcFrame()

        fragment = bytes.fromhex(FRAME_SHORT_INFO)[:7]
        for byte in fragment:
            frame.append(byte)

        assert frame.header is not None

        assert frame.header.frame_format is not None
        assert (
            frame.header.frame_format_type
            == (int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0xF000) >> 12
        )
        assert (
            frame.header.segmentation
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x800
        )
        assert (
            frame.header.frame_length
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x7FF
        )

        assert frame.header.destination_address == bytes.fromhex(
            FRAME_SHORT_INFO[2 * 2 : 3 * 2]
        )
        assert frame.header.source_address == bytes.fromhex(
            FRAME_SHORT_INFO[3 * 2 : 5 * 2]
        )
        assert frame.header.information_position == 8
        assert frame.header.control == int(FRAME_SHORT_INFO[5 * 2 : 6 * 2], 16)
        assert frame.header.header_check_sequence is None

    def test_read_header_check_sequence(self):
        """Test read past check sequence."""
        frame = hdlc.HdlcFrame()

        fragment = bytes.fromhex(FRAME_SHORT_INFO)[:8]
        for byte in fragment:
            frame.append(byte)

        assert frame.header is not None

        assert frame.header.frame_format is not None
        assert (
            frame.header.frame_format_type
            == (int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0xF000) >> 12
        )
        assert (
            frame.header.segmentation
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x800
        )
        assert (
            frame.header.frame_length
            == int(FRAME_SHORT_INFO[0 * 2 : 2 * 2], 16) & 0x7FF
        )

        assert frame.header.destination_address == bytes.fromhex(
            FRAME_SHORT_INFO[2 * 2 : 3 * 2]
        )
        assert frame.header.source_address == bytes.fromhex(
            FRAME_SHORT_INFO[3 * 2 : 5 * 2]
        )
        assert frame.header.information_position == 8
        assert frame.header.control == int(FRAME_SHORT_INFO[5 * 2 : 6 * 2], 16)
        assert frame.header.header_check_sequence == int(
            FRAME_SHORT_INFO[6 * 2 : 8 * 2], 16
        )


class TestHdlcFrame:
    """Test HdlcFrame."""

    def test_empty_frame(self):
        """Test empty frame."""
        frame = hdlc.HdlcFrame()

        assert frame.header is not None
        assert frame.as_bytes is not None
        assert len(frame.as_bytes) == 0
        assert len(frame) == 0
        assert frame.payload is None
        assert frame.frame_check_sequence is None
        assert frame.is_good_ffc is False
        assert frame.is_expected_length is False

    def test_empty_info_frame(self):
        """Test empty info frame."""
        frame = hdlc.HdlcFrame()

        frame_data = bytes.fromhex(FRAME_EMPTY_INFO)
        for byte in frame_data:
            frame.append(byte)

        assert frame.header is not None
        assert frame.as_bytes is not None
        assert len(frame.as_bytes) == len(frame_data)
        assert len(frame) == len(frame_data)
        assert frame.payload is None
        assert frame.frame_check_sequence == int(FRAME_EMPTY_INFO[-4:], 16)
        assert frame.is_good_ffc
        assert frame.is_expected_length

    def test_short_info_frame(self):
        """Test short info frame."""
        frame = hdlc.HdlcFrame()

        frame_data = bytes.fromhex(FRAME_SHORT_INFO)
        for byte in frame_data:
            frame.append(byte)

        assert frame.header is not None
        assert frame.as_bytes is not None
        assert len(frame.as_bytes) == len(frame_data)
        assert len(frame) == len(frame_data)
        assert frame.payload == bytes.fromhex(FRAME_SHORT_INFO)[-4:-2]
        assert frame.frame_check_sequence == int(FRAME_SHORT_INFO[-4:], 16)
        assert frame.is_good_ffc
        assert frame.is_expected_length


def test_long_hdlc_frame_with_format_a1() -> None:
    """Frames longer than 255 bytes have format byte 0xA1 (length bit 8 set)."""
    registers = [
        frames.aidon_register(f"1.0.{c}.7.0.255", frames.double_long_unsigned(c), 0, 27)
        for c in range(1, 16)
    ]
    information = frames.data_notification(frames.aidon_list(*registers))
    frame = frames.hdlc_frame(information)
    assert frame[1] == 0xA1

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(frame)

    assert len(read) == 1
    assert read[0].is_valid
    assert read[0].payload == information


@pytest.mark.xfail(
    reason="F16: flag octet in the HDLC header discards the frame", strict=True
)
def test_frame_with_flag_octet_as_length() -> None:
    information = frames.data_notification(frames.aidon_list())
    information += b"\x00" * (0x7E - 12 - len(information))
    frame = frames.hdlc_frame(information)
    assert frame[2] == 0x7E

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(frame)

    assert [f.as_bytes for f in read] == [frame[1:-1]]


def test_frame_ending_with_control_escape_is_not_aborted_without_octet_stuffing() -> (
    None
):
    """Without octet stuffing 0x7D is data, so a valid FCS may end with it."""
    frame = frames.aidon_frame_with_last_octet(0x7D)

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(frame)

    assert [f.as_bytes for f in read] == [frame[1:-1]]
    assert read[0].is_valid


def test_abort_sequence_without_octet_stuffing_warns_and_has_no_effect() -> None:
    frame = frames.aidon_frame_with_last_octet(0x7D)

    with pytest.warns(UserWarning, match="no effect without use_octet_stuffing"):
        reader = hdlc.HdlcFrameReader(use_octet_stuffing=False, use_abort_sequence=True)

    assert [f.as_bytes for f in reader.read(frame)] == [frame[1:-1]]


@pytest.mark.parametrize(
    ("stuffing", "abort"), [(False, False), (True, True), (True, False)]
)
def test_valid_combinations_give_no_warning(
    recwarn: pytest.WarningsRecorder, stuffing: bool, abort: bool
) -> None:
    hdlc.HdlcFrameReader(use_octet_stuffing=stuffing, use_abort_sequence=abort)

    assert not recwarn.list


def test_aborted_frame_is_returned_invalid_without_abort_sequence() -> None:
    frame = _stuff(frames.aidon_frame_with_last_octet(0x7D))

    read = hdlc.HdlcFrameReader(use_octet_stuffing=True).read(
        frame[:15] + b"\x7d\x7e" + frame[1:]
    )

    assert [f.is_valid for f in read] == [False, True]


def _stuff(frame: bytes, also_escape: bytes = b"") -> bytes:
    """Apply HDLC octet stuffing to a flagged frame."""
    out = bytearray()
    for octet in frame[1:-1]:
        if octet in (0x7E, 0x7D) or octet in also_escape:
            out += bytes([0x7D, octet ^ 0x20])
        else:
            out.append(octet)
    return b"\x7e" + bytes(out) + b"\x7e"


def test_stuffed_frame_with_escaped_last_fcs_octet_is_not_aborted() -> None:
    """0x5D may be sent escaped as 0x7D 0x7D; the closing flag is then no abort."""
    frame = frames.aidon_frame_with_last_octet(0x5D)
    stuffed = _stuff(frame, also_escape=b"\x5d")
    assert stuffed[-3:] == b"\x7d\x7d\x7e"

    read = hdlc.HdlcFrameReader(use_octet_stuffing=True, use_abort_sequence=True).read(
        stuffed
    )

    assert [f.as_bytes for f in read] == [frame[1:-1]]
    assert read[0].is_valid


def test_abort_right_after_opening_flag_does_not_corrupt_next_frame() -> None:
    frame = frames.aidon_frame_with_last_octet(0x7D)

    read = hdlc.HdlcFrameReader(use_octet_stuffing=True, use_abort_sequence=True).read(
        b"\x7e\x7d\x7e" + _stuff(frame)
    )

    assert [f.as_bytes for f in read] == [frame[1:-1]]
    assert read[0].is_valid


def test_aborting_flag_opens_next_frame() -> None:
    frame = _stuff(frames.aidon_frame_with_last_octet(0x7D))

    read = hdlc.HdlcFrameReader(use_octet_stuffing=True, use_abort_sequence=True).read(
        frame[:15] + b"\x7d\x7e" + frame[1:]
    )

    assert len(read) == 1
    assert read[0].is_valid


def test_repeated_aborts_do_not_grow_the_buffer() -> None:
    reader = hdlc.HdlcFrameReader(use_octet_stuffing=True, use_abort_sequence=True)
    fragment = b"\x7e" + bytes.fromhex("a0084102011037") + b"\x7d\x7e"

    for _ in range(1000):
        reader.read(fragment)

    assert len(reader._buffer._buffer) < 2 * len(fragment)


class TestReaderBuffer:
    """Edge cases of the internal byte buffer used by HdlcFrameReader."""

    @staticmethod
    def _filled(data: bytes, popped: int = 0) -> hdlc._ReaderBuffer:
        buffer = hdlc._ReaderBuffer()
        buffer.extend(data)
        for _ in range(popped):
            buffer.pop()
        return buffer

    @staticmethod
    def _rest(buffer: hdlc._ReaderBuffer) -> bytes:
        rest = bytearray()
        while buffer.is_available:
            rest.append(buffer.pop())
        return bytes(rest)

    def test_pop_on_empty_buffer_raises(self) -> None:
        buffer = hdlc._ReaderBuffer()

        assert not buffer.is_available
        with pytest.raises(IndexError):
            buffer.pop()

    @pytest.mark.parametrize(
        ("data", "popped", "expected"),
        [
            (b"\x7e\x01\x02", 0, b"\x7e\x01\x02"),  # flag first
            (b"\x01\x02\x7e\x03", 0, b"\x7e\x03"),  # flag in the middle
            (b"\x01\x02\x7e", 0, b"\x7e"),  # flag last
            (b"\x01\x02\x03", 0, b""),  # no flag
            (b"", 0, b""),  # empty
            (b"\x7e\x01\x7e\x02", 1, b"\x7e\x02"),  # flag before position is consumed
            (b"\x7e\x01\x02", 3, b""),  # everything consumed
        ],
        ids=[
            "first",
            "middle",
            "last",
            "none",
            "empty",
            "consumed-flag",
            "all-consumed",
        ],
    )
    def test_trim_buffer_to_flag_or_end(
        self, data: bytes, popped: int, expected: bytes
    ) -> None:
        buffer = self._filled(data, popped)

        buffer.trim_buffer_to_flag_or_end()

        assert self._rest(buffer) == expected

    def test_trim_to_current_position_keeps_unread_and_accepts_more(self) -> None:
        buffer = self._filled(b"\x01\x02\x03", popped=2)

        buffer.trim_buffer_to_current_position()
        buffer.extend(b"\x04")

        assert self._rest(buffer) == b"\x03\x04"

    def test_trim_when_everything_is_read(self) -> None:
        buffer = self._filled(b"\x01\x02", popped=2)

        buffer.trim_buffer_to_current_position()

        assert not buffer.is_available
        buffer.extend(b"\x03")
        assert self._rest(buffer) == b"\x03"


_buffer_operation = st.one_of(
    # a small alphabet makes flags (0x7E) common at every position
    st.tuples(
        st.just("extend"),
        st.lists(st.sampled_from([0x01, 0x7D, 0x7E]), max_size=6).map(bytes),
    ),
    st.tuples(st.just("pop"), st.none()),
    st.tuples(st.just("trim_current"), st.none()),
    st.tuples(st.just("trim_flag"), st.none()),
)


@given(operations=st.lists(_buffer_operation, max_size=60))
def test_reader_buffer_matches_simple_model(
    operations: list[tuple[str, bytes | None]],
) -> None:
    """The buffer behaves like a plain byte string with a read position."""
    buffer = hdlc._ReaderBuffer()
    unread = b""  # model: the bytes that are not read yet

    for operation, data in operations:
        if operation == "extend":
            assert data is not None
            buffer.extend(data)
            unread += data
        elif operation == "pop":
            if unread:
                assert buffer.pop() == unread[0]
                unread = unread[1:]
        elif operation == "trim_current":
            buffer.trim_buffer_to_current_position()
        else:
            buffer.trim_buffer_to_flag_or_end()
            flag = unread.find(b"\x7e")
            unread = b"" if flag == -1 else unread[flag:]
        assert buffer.is_available == bool(unread)

    assert TestReaderBuffer._rest(buffer) == unread


def test_dangling_escape_before_flag_does_not_corrupt_next_frame() -> None:
    """With stuffing but without abort handling, a lone escape before a flag is dropped."""
    frame = _stuff(frames.aidon_frame_with_last_octet(0x7D))
    reader = hdlc.HdlcFrameReader(use_octet_stuffing=True)

    assert reader.read(b"\x7e\x7d") == []
    assert reader.read(b"\x7e") == []
    read = reader.read(frame[1:])

    assert len(read) == 1
    assert read[0].is_valid


# Recovery after a broken frame: the reader must resynchronise on the flag that ends it.
# Without octet stuffing a truncated frame has no closing flag of its own: the flag that
# "ends" it is the opening flag of the next frame. Today that flag is either read as data
# (truncated after the length field; the reader waits until MAX_FRAME_LENGTH) or skipped
# by hunt mode (truncated before the header is complete), so following frames are lost.


def _aidon_frame() -> bytes:
    frame = frames.hdlc_frame(
        frames.data_notification(
            frames.aidon_list(
                frames.aidon_register(
                    "1.0.1.7.0.255", frames.double_long_unsigned(42), 0, 27
                )
            )
        )
    )
    assert 0x7E not in frame[1:-1] and 0x7D not in frame[1:-1]
    return frame


def _valid(read: list[hdlc.HdlcFrame]) -> list[bytes]:
    return [f.as_bytes for f in read if f.is_good_ffc and f.is_expected_length]


@pytest.mark.parametrize("cut", [5, 9, 20, 30])
@pytest.mark.parametrize("chunked", [False, True])
def test_frames_after_truncated_frame_are_recovered(cut: int, chunked: bool) -> None:
    frame = _aidon_frame()
    stream = frame[:cut] + frame * 5
    reader = hdlc.HdlcFrameReader(use_octet_stuffing=False)

    if chunked:
        read = [f for b in stream for f in reader.read(bytes([b]))]
    else:
        read = reader.read(stream)

    assert _valid(read) == [frame[1:-1]] * 5


def test_frames_with_shared_flags_after_truncated_frame_are_recovered() -> None:
    frame = _aidon_frame()
    shared = frame + frame[1:] * 4  # one flag between frames
    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(frame[:20] + shared)

    assert _valid(read) == [frame[1:-1]] * 5


@pytest.mark.parametrize("use_octet_stuffing", [False, True])
def test_too_short_frame_does_not_cost_the_next_frame(
    use_octet_stuffing: bool,
) -> None:
    frame = _aidon_frame()
    reader = hdlc.HdlcFrameReader(use_octet_stuffing=use_octet_stuffing)

    read = reader.read(b"\x7e\xa0\x2a\x41" + frame)

    assert _valid(read) == [frame[1:-1]]


def test_frames_after_garbage_claiming_max_length_are_recovered() -> None:
    frame = _aidon_frame()
    # A complete header (format field claiming 2047 octets, addresses, control, HCS),
    # so the following frames are swallowed until the maximum length is reached.
    garbage = b"\x7e\xa7\xff\x41\x08\x83\x13\x00\x00"
    filler = b"\x00" * (hdlc.HdlcFrame.MAX_FRAME_LENGTH + 10)

    reader = hdlc.HdlcFrameReader(use_octet_stuffing=False)

    assert reader.read(garbage + frame * 5) == []  # swallowed for now
    read = reader.read(filler + frame)

    assert _valid(read) == [frame[1:-1]] * 6


def test_valid_frame_inside_invalid_frame_is_recovered() -> None:
    frame = _aidon_frame()
    # A broken frame whose length field makes the flag that closes `frame` look like
    # its own closing flag: 19 octets + the flag of `frame` + `frame` without flags.
    target = 19 + 1 + (len(frame) - 2)
    broken = frames.hdlc_frame(b"\x00" * (target - 10))
    assert len(broken) - 2 == target and 0x7E not in broken[1:20]

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(broken[:20] + frame)

    assert len(read) == 2
    assert not read[0].is_valid  # the broken frame is still reported as invalid
    assert _valid(read) == [frame[1:-1]]


# Edge cases of recovery after a broken frame.


def _aidon_frame_with_value(value: int) -> bytes:
    return frames.hdlc_frame(
        frames.data_notification(
            frames.aidon_list(
                frames.aidon_register(
                    "1.0.1.7.0.255", frames.double_long_unsigned(value), 0, 27
                )
            )
        )
    )


def test_frame_missing_only_its_closing_flag_shares_the_next_opening_flag() -> None:
    frame = _aidon_frame()

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(frame[:-1] + frame)

    assert _valid(read) == [frame[1:-1]] * 2


def test_consecutive_truncated_frames_do_not_cost_following_frames() -> None:
    frame = _aidon_frame()
    stream = frame[:20] + frame[:5] + frame[:30] + frame[:9] + frame * 3

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(stream)

    assert _valid(read) == [frame[1:-1]] * 3


@pytest.mark.parametrize("length", [0, 1, 2, 3, 8, 9])
def test_degenerate_length_field_does_not_cost_following_frames(length: int) -> None:
    frame = _aidon_frame()
    garbage = (
        b"\x7e" + (0xA000 | length).to_bytes(2, "big") + b"\x41\x08\x83\x13\x00\x00"
    )

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(garbage + frame * 2)

    assert _valid(read) == [frame[1:-1]] * 2


def test_frame_with_flag_octets_in_data_after_truncated_frame() -> None:
    frame = _aidon_frame_with_value(0x7E7E7E7E)
    assert frame[1:-1].count(0x7E) == 4

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(frame[:20] + frame * 3)

    assert _valid(read) == [frame[1:-1]] * 3


def test_frame_with_flag_octets_in_data_inside_invalid_frame_of_expected_length() -> (
    None
):
    frame = _aidon_frame_with_value(0x7E7E7E7E)
    target = 19 + 1 + (len(frame) - 2)
    broken = frames.hdlc_frame(b"\x00" * (target - 10))
    assert 0x7E not in broken[1:20]

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(broken[:20] + frame)

    assert _valid(read) == [frame[1:-1]]


def test_corrupted_frame_with_flag_in_data_does_not_cost_following_frames() -> None:
    frame = _aidon_frame_with_value(0x7E7E7E7E)
    corrupted = bytearray(frame)
    corrupted[-3] ^= 0xFF  # wrong FCS, same length

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(
        bytes(corrupted) + frame * 2
    )

    assert len(read) >= 3
    assert not read[0].is_good_ffc
    assert _valid(read) == [frame[1:-1]] * 2


def test_valid_frame_is_not_read_again() -> None:
    # A valid frame with flag octets in its data must be returned once, and the flags
    # inside it must not start extra frames.
    frame = _aidon_frame_with_value(0x7E7E7E7E)

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(frame * 3)

    assert [f.as_bytes for f in read] == [frame[1:-1]] * 3


def test_truncated_stuffed_frame_does_not_cost_the_next_frame() -> None:
    frame = _aidon_frame()
    reader = hdlc.HdlcFrameReader(use_octet_stuffing=True)

    read = reader.read(frame[:30] + frame)

    assert len(read) == 2
    assert not read[0].is_good_ffc
    assert _valid(read) == [frame[1:-1]]


def test_reader_buffer_stays_bounded_with_garbage() -> None:
    import random

    rnd = random.Random(20261127)
    frame = _aidon_frame()
    reader = hdlc.HdlcFrameReader(use_octet_stuffing=False)
    valid = 0
    for _ in range(100):
        chunk = bytes(rnd.choice(b"\x7e\xa0\xa7\x00\xff\x41") for _ in range(400))
        valid += len(_valid(reader.read(chunk + frame)))
        # Unread octets are kept in the buffer and octets of a frame being read in
        # the frame: neither can grow past what one frame can hold.
        assert len(reader._buffer._buffer) <= hdlc.HdlcFrame.MAX_FRAME_LENGTH + 500
        assert len(reader._raw_frame_data) <= hdlc.HdlcFrame.MAX_FRAME_LENGTH + 1
    assert valid > 0
