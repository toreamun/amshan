import tests.test_aidon
import tests.test_kaifa
import tests.test_kamstrup
from smartmeterdecode import autodecoder


def test_decode_frame():
    decoder = autodecoder.AutoDecoder()
    assert decoder.previous_success_decoder is None

    decoded = decoder.decode_frame(tests.test_kamstrup.list_1_three_phase)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder is "Kamstrup"

    decoded = decoder.decode_frame(tests.test_kamstrup.list_2_three_phase)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder is "Kamstrup"

    decoded = decoder.decode_frame(tests.test_aidon.list_1)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder is "Aidon"

    decoded = decoder.decode_frame(tests.test_kaifa.list_1)
    assert isinstance(decoded, dict)
    assert decoder.previous_success_decoder is "Kaifa"

    decoded = decoder.decode_frame(bytes([1, 2, 3, 4, 5]))
    assert decoded is None
    assert decoder.previous_success_decoder is "Kaifa"
