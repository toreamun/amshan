from typing import List

import construct

from smartmeterdecode import cosem as cosem
from smartmeterdecode import obis_map as obis_map

NotificationBody: construct.Struct
LlcPdu: construct.Struct

def normalize_parsed_frame(frame: construct.Struct) -> dict: ...
def decode_frame(frame: bytes) -> dict: ...
