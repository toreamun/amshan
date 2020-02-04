import construct
from readams.meterdecode import aidon
from readams.meterdecode import kaifa
from readams.meterdecode import kamstrup


class AutoDecoder:
    _decoder_functions = [aidon.decode_frame, kaifa.decode_frame, kamstrup.decode_frame]

    def __init__(self):
        self.__previous_success = 0

    def decode_frame(self, frame: bytes) -> dict:
        for i in range(len(AutoDecoder._decoder_functions)):
            index = (i + self.__previous_success) % len(AutoDecoder._decoder_functions)
            decoder = AutoDecoder._decoder_functions[index]
            try:
                decoded = decoder(frame)
                self.__previous_success = index
                return decoded
            except construct.ConstructError:
                pass

        return None
