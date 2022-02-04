"""Use this module to easily decode any supported meter message format."""
from __future__ import annotations

from datetime import datetime
from typing import cast

import construct  # type: ignore

from amshan import aidon, dlde, kaifa, kamstrup
from amshan.common import MeterMessageBase


class AutoDecoder:
    """
    Use this class to easily decode any supported meter message formats into a common dictionary format.

    The class tries all decoders until success or no more decoders.
    The successful decoder is stored and tried as the first decoder next time.
    """

    payload_decoder_functions = [
        ("Aidon", aidon.decode_frame_content),
        ("Kaifa", kaifa.decode_frame_content),
        ("Kamstrup", kamstrup.decode_frame_content),
        ("P1", dlde.decode_p1_readout_content),
    ]

    def __init__(self) -> None:
        """Initialize AutoDecoder."""
        self.__previous_success: int | None = None

    @property
    def previous_success_decoder(self) -> str | None:
        """Return the name of the previous successful decoder function, or None if none previous success."""
        if self.__previous_success is not None:
            decoder_name, _ = AutoDecoder.payload_decoder_functions[
                self.__previous_success
            ]
            return decoder_name
        return None

    def decode_message_payload(
        self, payload: bytes
    ) -> dict[str, str | int | float | datetime] | None:
        """
        Decode meter message payload as a dictionary.

        The previous meter decoder used with success is used first. Then other meter decoders are tried.
        :rtype: dictionary or None if none of the decoders worked.
        """
        previous_success_index = (
            self.__previous_success if self.__previous_success else 0
        )

        for i in range(len(AutoDecoder.payload_decoder_functions)):
            index = (i + previous_success_index) % len(
                AutoDecoder.payload_decoder_functions
            )
            _, decoder = AutoDecoder.payload_decoder_functions[index]
            try:
                decoded = decoder(payload)
                self.__previous_success = index
                return decoded
            except (construct.ConstructError, ValueError):
                pass

        return None

    def decode_message(
        self, message: MeterMessageBase
    ) -> dict[str, str | int | float | datetime] | None:
        """
        Decode meter message as a dictionary.

        The previous meter decoder used with success is used first. Then other meter decoders are tried.
        :rtype: dictionary or None if none of the decoders worked.
        """
        if not message.payload:
            return None

        previous_success_index = (
            self.__previous_success if self.__previous_success else 0
        )

        for i in range(len(AutoDecoder.payload_decoder_functions)):
            index = (i + previous_success_index) % len(
                AutoDecoder.payload_decoder_functions
            )
            name, decoder = AutoDecoder.payload_decoder_functions[index]
            try:

                decoded = (
                    dlde.decode_p1_readout(cast(dlde.DataReadout, message))
                    if name == "P1" and isinstance(message, dlde.DataReadout)
                    else decoder(message.payload)
                )
                self.__previous_success = index
                return decoded
            except (construct.ConstructError, ValueError):
                pass

        return None
