"""Autodecoder tests."""
from __future__ import annotations

from han import autodecoder
from han.dlde import DataReadout

import tests.test_aidon
import tests.test_dlde
import tests.test_kaifa
import tests.test_kamstrup


def test_decode_frame():
    """Test AutoDecoder."""
    decoder = autodecoder.AutoDecoder()
    assert decoder.previous_success_decoder is None

    decoded = decoder.decode_message_payload(tests.test_kamstrup.no_list_1_three_phase)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder == "Kamstrup"

    decoded = decoder.decode_message_payload(tests.test_kamstrup.no_list_2_three_phase)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder == "Kamstrup"

    decoded = decoder.decode_message_payload(tests.test_aidon.no_list_1)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder == "Aidon"

    decoded = decoder.decode_message_payload(tests.test_kaifa.no_list_1)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder == "Kaifa"

    decoded = decoder.decode_message_payload(bytes([1, 2, 3, 4, 5]))
    assert decoded is None
    assert decoder.previous_success_decoder == "Kaifa"


def test_decode_message():
    """Test AutoDecoder."""
    decoder = autodecoder.AutoDecoder()
    decoded = decoder.decode_message(
        DataReadout(tests.test_dlde.EXAMPLE_DATA_A_LANDISGYR_360)
    )
    assert decoded
