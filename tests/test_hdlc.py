"""HDLC tests."""
# pylint: disable = no-self-use
from __future__ import annotations

import pytest
from amshan import hdlc

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
        assert not frames[0].header.header_check_sequence is None
        assert frames[0].payload is None

    def test_too_short_frame_is_discarded(self):
        """Test that too short frame is discarded."""
        data_feed = bytes.fromhex(FLAG_SEQUENCE + "a0080102011037" + FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 0

    def test_abort_sequence(self):
        """Test abort sequence."""
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE + FRAME_SHORT_INFO + CONTROL_ESCAPE + FLAG_SEQUENCE
        )

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 0

    def test_single_flag_sequences_between_frames(self):
        """Test single flag seqeunce between frames."""
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
        assert not frames[0].header.header_check_sequence is None
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
        assert frame.frame_data is not None
        assert len(frame.frame_data) == 0
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
        assert frame.frame_data is not None
        assert len(frame.frame_data) == len(frame_data)
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
        assert frame.frame_data is not None
        assert len(frame.frame_data) == len(frame_data)
        assert len(frame) == len(frame_data)
        assert frame.payload == bytes.fromhex(FRAME_SHORT_INFO)[-4:-2]
        assert frame.frame_check_sequence == int(FRAME_SHORT_INFO[-4:], 16)
        assert frame.is_good_ffc
        assert frame.is_expected_length
