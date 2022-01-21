"""Autodecoder tests."""
import tests.test_aidon
import tests.test_kaifa
import tests.test_kamstrup
from amshan import autodecoder


def test_decode_frame():
    """Test AutoDecoder."""
    decoder = autodecoder.AutoDecoder()
    assert decoder.previous_success_decoder is None

    decoded = decoder.decode_frame_content(tests.test_kamstrup.list_1_three_phase)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder == "Kamstrup"

    decoded = decoder.decode_frame_content(tests.test_kamstrup.list_2_three_phase)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder == "Kamstrup"

    decoded = decoder.decode_frame_content(tests.test_aidon.no_list_1)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder == "Aidon"

    decoded = decoder.decode_frame_content(tests.test_kaifa.no_list_1)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder == "Kaifa"

    decoded = decoder.decode_frame_content(bytes([1, 2, 3, 4, 5]))
    assert decoded is None
    assert decoder.previous_success_decoder == "Kaifa"
