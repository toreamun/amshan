"""Use this module to easily decode any supported meter frame format."""
from datetime import datetime
from typing import Dict, Optional, Union

import construct  # type: ignore

from amshan import aidon, kaifa, kamstrup


class AutoDecoder:
    """
    Use this class to easily decode any supported meter frame formats into a common dictionary format.

    The class tries all decoders until success or no more decoders.
    The successful decoder is stored and tried as the first decoder next time.
    """

    decoder_functions = [
        ("Aidon", aidon.decode_frame_content),
        ("Kaifa", kaifa.decode_frame_content),
        ("Kamstrup", kamstrup.decode_frame_content),
    ]

    def __init__(self) -> None:
        """Initialize AutoDecoder."""
        self.__previous_success: Optional[int] = None

    @property
    def previous_success_decoder(self) -> Optional[str]:
        """Return the name of the previous successful decoder function, or None if none previous success."""
        if self.__previous_success is not None:
            decoder_name, _ = AutoDecoder.decoder_functions[self.__previous_success]
            return decoder_name
        return None

    def decode_frame_content(
        self, frame_content: bytes
    ) -> Optional[Dict[str, Union[str, int, float, datetime]]]:
        """
        Decode meter LLC PDU frame content as a dictionary.

        The previous meter decoder used with success is used first. Then other meter decoders are tried.
        :rtype: dictionary or None if none of the decoders worked.
        """
        previous_success_index = (
            self.__previous_success if self.__previous_success else 0
        )

        for i in range(len(AutoDecoder.decoder_functions)):
            index = (i + previous_success_index) % len(AutoDecoder.decoder_functions)
            _, decoder = AutoDecoder.decoder_functions[index]
            try:
                decoded_frame = decoder(frame_content)
                self.__previous_success = index
                return decoded_frame
            except construct.ConstructError:
                pass

        return None
