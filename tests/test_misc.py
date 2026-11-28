"""Tests for behavior not covered by the meter specific test modules."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

import pytest

from han import dlde, hdlc
from han.autodecoder import AutoDecoder
from han.common import DlmsMessage, MeterMessageType
from han.meter_connection import ConnectionManager
from han.obis import Obis
from tests import frames

AIDON_INFORMATION = frames.data_notification(
    frames.aidon_list(
        frames.aidon_register("1.0.1.7.0.255", frames.double_long_unsigned(42), 0, 27)
    )
)


class TestDlmsMessage:
    """DlmsMessage."""

    def test_properties(self) -> None:
        message = DlmsMessage(AIDON_INFORMATION)

        assert message.message_type == MeterMessageType.DLMS
        assert message.is_valid
        assert message.as_bytes == AIDON_INFORMATION
        assert message.payload == AIDON_INFORMATION

    def test_minimum_length_is_valid(self) -> None:
        assert DlmsMessage(b"\x00\x01\x02\x03\x04").is_valid

    def test_too_short_is_invalid(self) -> None:
        assert not DlmsMessage(b"\x00\x01\x02\x03").is_valid


class TestAutoDecoder:
    """AutoDecoder."""

    def test_unknown_payload_gives_none(self) -> None:
        decoder = AutoDecoder()

        assert decoder.decode_message_payload(b"\x01\x02\x03") is None
        assert decoder.decode_message(DlmsMessage(b"\x01\x02\x03\x04\x05")) is None
        assert decoder.previous_success_decoder is None

    def test_empty_message_gives_none(self) -> None:
        assert AutoDecoder().decode_message(DlmsMessage(b"")) is None

    def test_remembers_successful_decoder(self) -> None:
        decoder = AutoDecoder()
        readout = dlde.DataReadout(
            frames.p1_readout("ABC5TEST", ["1-0:1.7.0(00.042*kW)"])
        )

        assert decoder.decode_message(readout) == {
            "active_power_import": 42,
            "meter_manufacturer_id": "ABC",
            "meter_type_id": "TEST",
        }
        assert decoder.previous_success_decoder == "P1"
        assert decoder.decode_message_payload(AIDON_INFORMATION) == {
            "meter_manufacturer": "Aidon",
            "active_power_import": 42,
        }
        assert decoder.previous_success_decoder == "Aidon_frame"


class TestDataReadout:
    """dlde.DataReadout and P1 decoding."""

    def test_must_start_with_slash(self) -> None:
        with pytest.raises(ValueError, match="start"):
            dlde.DataReadout(b"ABC5TEST\r\n!")

    def test_must_have_end_line(self) -> None:
        with pytest.raises(ValueError, match="end line"):
            dlde.DataReadout(b"/ABC5TEST\r\n\r\n1-0:1.7.0(01.000*kW)\r\n")

    def test_wrong_checksum_is_invalid(self) -> None:
        readout = frames.p1_readout("ABC5TEST", ["1-0:1.7.0(01.000*kW)"])

        assert not dlde.DataReadout(readout.replace(b"01.000", b"02.000")).is_valid

    def test_readout_without_checksum_is_valid(self) -> None:
        readout = dlde.DataReadout(b"/ABC5TEST\r\n\r\n1-0:1.7.0(01.000*kW)\r\n!\r\n")

        assert readout.expected_checksum is None
        assert readout.is_valid
        assert readout.end_line == "!"

    def test_lines_and_identification(self) -> None:
        readout = dlde.DataReadout(
            frames.p1_readout("ABC5TEST", ["1-0:1.7.0(01.000*kW)", "0-0:96.1.0(123)"])
        )

        assert readout.data_lines == ["1-0:1.7.0(01.000*kW)", "0-0:96.1.0(123)"]
        assert readout.identification_line.manufacturer_id == "ABC"
        assert readout.identification_line.identification == "TEST"
        assert len(readout) == len(readout.as_bytes)
        assert str(readout).startswith("/ABC5TEST")

    def test_value_units_and_unknown_codes(self) -> None:
        decoded = dlde.decode_p1_readout_content(
            b"1-0:32.7.0(229.9*V)\r\n"
            b"1-0:31.7.0(001.5*A)\r\n"
            b"1-0:1.8.0(00012.345*kWh)\r\n"
            b"1-0:99.99.0(abc)\r\n"
            b"0-0:1.0.0(261125213000W)\r\n"
        )

        assert decoded["voltage_l1"] == 229.9
        assert decoded["current_l1"] == 1.5
        assert decoded["active_power_import_total"] == 12345
        assert decoded["99.99.0"] == "abc"
        meter_datetime = decoded["meter_datetime"]
        assert isinstance(meter_datetime, datetime)
        assert meter_datetime.isoformat() == "2026-11-25T21:30:00"

    def test_multiple_unit_separators(self) -> None:
        with pytest.raises(ValueError, match="multiple"):
            dlde.DataSetValue.parse("1*kW*h")

    def test_empty_content(self) -> None:
        with pytest.raises(ValueError, match="no readout data"):
            dlde.decode_p1_readout_content(b"\r\n")

    def test_non_ascii_content(self) -> None:
        with pytest.raises(ValueError, match="ascii"):
            dlde.parse_p1_readout_content("1-0:1.7.0(1æ)".encode())


class TestObis:
    """han.obis."""

    def test_groups(self) -> None:
        code = Obis.from_string("1.0.31.7.0.255")

        assert (code.a, code.b, code.c, code.d, code.e, code.f) == (1, 0, 31, 7, 0, 255)
        assert code.as_tupple() == (1, 0, 31, 7, 0, 255)
        assert code.to_group_cdr_str() == "31.7.0"
        assert code.filter_group_cde().as_tupple() == (None, None, 31, 7, 0, None)

    def test_reduced_code(self) -> None:
        assert Obis.from_string("1-0:31.7.0").as_tupple() == (1, 0, 31, 7, 0, None)
        assert Obis.from_string("31.7").as_tupple() == (None, None, 31, 7, None, None)

    def test_invalid_code(self) -> None:
        with pytest.raises(ValueError, match="Not a valid obis code"):
            Obis.from_string("not obis")

    def test_equality_and_hash(self) -> None:
        code = Obis.from_string("1.1.31.7.1.255")

        assert code == Obis.from_string("1.1.31.7.1.255")
        assert code == "1.1.31.7.1.255"
        assert code != "not obis"
        assert hash(code) == hash(Obis.from_string("1.1.31.7.1.255"))
        assert repr(code) == "1.1.31.7.1.255"


class TestHdlcFrameReader:
    """HDLC reader behavior not covered by test_hdlc."""

    def test_invalid_frame_is_logged(self, caplog: pytest.LogCaptureFixture) -> None:
        broken = bytearray(frames.hdlc_frame(AIDON_INFORMATION))
        broken[-3] ^= 0xFF
        reader = hdlc.HdlcFrameReader(use_octet_stuffing=False)

        read = reader.read(bytes(broken))
        with caplog.at_level(logging.WARNING):
            assert not read[0].is_valid

        assert "Got invalid frame" in caplog.text

    def test_abort_sequence_discards_frame_with_octet_stuffing(self) -> None:
        frame = frames.hdlc_frame(AIDON_INFORMATION)
        assert 0x7D not in frame and 0x7E not in frame[1:-1]  # no stuffing needed
        reader = hdlc.HdlcFrameReader(use_octet_stuffing=True, use_abort_sequence=True)

        assert reader.is_in_hunt_mode
        assert reader.read(frame[:20] + b"\x7d\x7e") == []
        assert not reader.unescape_next
        assert len(reader.read(frame)) == 1


async def test_cancel_connect_loop_while_connecting() -> None:
    started = asyncio.Event()

    async def hanging_factory() -> None:
        started.set()
        await asyncio.sleep(3600)

    manager = ConnectionManager(hanging_factory)  # type: ignore[arg-type]
    loop_task = asyncio.create_task(manager.connect_loop())
    await asyncio.wait_for(started.wait(), 2)

    loop_task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await loop_task
