import pytest

from meterdecode import hdlc

FLAG_SEQUENCE = "7e"
CONTROL_ESCAPE = "7d"

FRAME_EMPTY_INFO = "a00801020110378d"
FRAME_SHORT_INFO = "a00C0102011027a00201e7de"
FRAME_WITH_ESCAPE_CHARACTER_IN_INFO = \
    "a02a410883130413e6e7000f40000000000101020309060100010700ff060000067d02020f00161b1c05"
FRAME_WITH_FLAG_SEQUENCE_CHARACTER_IN_INFO = \
    "a027010201105a87e6e7000f40000000090c07e4020f06011922ff8000000201060000157eea5e"
STUFFED_FRAME_SHORT_INFO = "a00d0102011063ab7d5e7d5d7d23932D"


class TestHdlcFrameReader:

    def test_frame_with_escape_character(self):
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE +
            FRAME_WITH_ESCAPE_CHARACTER_IN_INFO +
            FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader(False)
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 1
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].information == bytes.fromhex(FRAME_WITH_ESCAPE_CHARACTER_IN_INFO)[8:-2]

    def test_frame_with_control_caracter_in_content(self):
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE +
            FRAME_WITH_FLAG_SEQUENCE_CHARACTER_IN_INFO +
            FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader(False)
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 1
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].information == bytes.fromhex(FRAME_WITH_FLAG_SEQUENCE_CHARACTER_IN_INFO)[8:-2]

    @pytest.mark.parametrize("data_feed", [
        bytes.fromhex("c3" + FLAG_SEQUENCE + FRAME_SHORT_INFO + FLAG_SEQUENCE),
        bytes.fromhex("0600001fc7cec3" + FLAG_SEQUENCE + FRAME_SHORT_INFO + FLAG_SEQUENCE)
    ])
    def test_start_read_in_frame(self, data_feed):
        frame_reader = hdlc.HdlcFrameReader(False)
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 1
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].information == bytes.fromhex(FRAME_SHORT_INFO)[8:-2]

    def test_empty_info_frame(self):
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE +
            FRAME_EMPTY_INFO +
            FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 1
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert not frames[0].header.header_check_sequence is None
        assert frames[0].information is None

    def test_too_short_frame_is_discarded(self):
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE +
            "a0080102011037" +
            FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 0

    def test_abort_sequence(self):
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE +
            FRAME_SHORT_INFO +
            CONTROL_ESCAPE +
            FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 0

    def test_single_flag_sequences_between_frames(self):
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE +
            FRAME_SHORT_INFO +
            FLAG_SEQUENCE +
            FRAME_EMPTY_INFO +
            FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 2
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].information == bytes.fromhex(FRAME_SHORT_INFO)[8:-2]
        assert frames[1].is_good_ffc
        assert frames[1].is_expected_length
        assert frames[1].information is None

    def test_two_flag_sequences_between_frames(self):
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE +
            FRAME_SHORT_INFO +
            FLAG_SEQUENCE + FLAG_SEQUENCE +
            FRAME_EMPTY_INFO +
            FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 2
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].information == bytes.fromhex(FRAME_SHORT_INFO)[8:-2]
        assert frames[1].is_good_ffc
        assert frames[1].is_expected_length
        assert frames[1].information is None

    def test_many_flag_sequences_between_frames(self):
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE +
            FRAME_SHORT_INFO +
            FLAG_SEQUENCE + FLAG_SEQUENCE + FLAG_SEQUENCE + FLAG_SEQUENCE + FLAG_SEQUENCE + FLAG_SEQUENCE +
            FRAME_EMPTY_INFO +
            FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader()
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 2
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert frames[0].information == bytes.fromhex(FRAME_SHORT_INFO)[8:-2]
        assert frames[1].is_good_ffc
        assert frames[1].is_expected_length
        assert frames[1].information is None

    def test_stuffed_frame_short_info(self):
        data_feed = bytes.fromhex(
            FLAG_SEQUENCE +
            STUFFED_FRAME_SHORT_INFO +
            FLAG_SEQUENCE)

        frame_reader = hdlc.HdlcFrameReader(True)
        frames = frame_reader.read(data_feed)

        assert frames is not None
        assert len(frames) == 1
        assert frames[0].is_good_ffc
        assert frames[0].is_expected_length
        assert not frames[0].header.header_check_sequence is None
        assert frames[0].information == bytes.fromhex("7e7d03")
