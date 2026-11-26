"""Tests for the synthetic frame builders in tests/frames.py."""

from __future__ import annotations

from han import aidon, dlde, hdlc
from tests import frames
from tests.test_hdlc import FRAME_WITH_ESCAPE_CHARACTER_IN_INFO


def test_hdlc_frame_matches_known_frame() -> None:
    """Builder reproduces a known frame byte by byte."""
    known = bytes.fromhex(FRAME_WITH_ESCAPE_CHARACTER_IN_INFO)

    assert frames.hdlc_frame(known[8:-2], flags=False) == known


def test_hdlc_frame_is_read_as_valid() -> None:
    """A built frame is read as a valid HDLC frame with the same payload."""
    information = frames.data_notification(
        frames.aidon_list(
            frames.aidon_register(
                "1.0.1.7.0.255", frames.double_long_unsigned(1234), 0, 27
            )
        )
    )

    read = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(
        frames.hdlc_frame(information)
    )

    assert len(read) == 1
    assert read[0].is_valid
    assert read[0].payload == information
    assert aidon.decode_frame_content(read[0].payload) == {
        "meter_manufacturer": "Aidon",
        "active_power_import": 1234,
    }


def test_p1_readout_is_valid() -> None:
    """A built P1 readout has a checksum accepted by DataReadout."""
    readout = dlde.DataReadout(frames.p1_readout("ABC5TEST", ["1-0:1.7.0(01.234*kW)"]))

    assert readout.is_valid
    assert dlde.decode_p1_readout(readout)["active_power_import"] == 1234
