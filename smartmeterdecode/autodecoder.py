from typing import Optional

import construct

from smartmeterdecode import aidon, kaifa, kamstrup


class AutoDecoder:
    _decoder_functions = [
        ("Aidon", aidon.decode_frame),
        ("Kaifa", kaifa.decode_frame),
        ("Kamstrup", kamstrup.decode_frame),
    ]

    def __init__(self):
        self.__previous_success = None

    @property
    def previous_success_decoder(self):
        if self.__previous_success is not None:
            decoder_name, _ = AutoDecoder._decoder_functions[self.__previous_success]
            return decoder_name
        return None

    def decode_frame(self, frame: bytes) -> Optional[dict]:
        previous_success_index = (
            self.__previous_success if self.__previous_success else 0
        )

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
