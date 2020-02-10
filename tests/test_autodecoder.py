import tests.test_aidon
import tests.test_kamstrup
from meterdecode import autodecoder


def test_decode_frame():
    decoder = autodecoder.AutoDecoder()
    decoder.decode_frame(tests.test_kamstrup.list_1_three_phase)
    decoder.decode_frame(tests.test_kamstrup.list_2_three_phase)
    decoder.decode_frame(tests.test_aidon.list_1)
