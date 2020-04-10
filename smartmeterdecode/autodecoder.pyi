from typing import Optional

from smartmeterdecode import aidon as aidon
from smartmeterdecode import kaifa as kaifa
from smartmeterdecode import kamstrup as kamstrup

class AutoDecoder:
    def __init__(self) -> None: ...
    @property
    def previous_success_decoder(self) -> Optional[str]: ...
    def decode_frame(self, frame: bytes) -> Optional[dict]: ...
