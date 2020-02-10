import construct

from meterdecode import kaifa, kamstrup, aidon


class AutoDecoder:
    _decoder_functions = [
        ("aidon", aidon.decode_frame),
        ("kaifa", kaifa.decode_frame),
        ("kamstrup", kamstrup.decode_frame)]

    def __init__(self):
        self.__previous_success = None

    @property
    def previous_decoder_name(self):
        if self.__previous_success is not None:
            decoder_name, _ = AutoDecoder._decoder_functions[self.__previous_success]
            return decoder_name
        return None

    def decode_frame(self, frame: bytes) -> dict:
        previous_success_index = self.__previous_success if self.__previous_success else 0

        for i in range(len(AutoDecoder._decoder_functions)):
            index = (i + previous_success_index) % len(AutoDecoder._decoder_functions)
            _, decoder = AutoDecoder._decoder_functions[index]
            try:
                decoded_frame = decoder(frame)
                self.__previous_success = index
                return decoded_frame
            except construct.ConstructError:
                pass

        return None
