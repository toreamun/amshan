"""Decoding support for Aidon meters."""
from datetime import datetime
from typing import Dict, Union

import construct  # type: ignore

from amshan import cosem, obis_map

Element: construct.Struct = construct.Struct(
    construct.Const(
        cosem.CommonDataTypes.structure, cosem.CommonDataTypes
    ),  # expect structure
    "length" / construct.Int8ub,
    "obis" / cosem.ObisCodeOctedStringField,
    "content_type" / cosem.CommonDataTypes,
    "content"
    / construct.Switch(
        construct.this.content_type,
        {
            cosem.CommonDataTypes.visible_string: cosem.VisibleString,
            cosem.CommonDataTypes.octet_string: cosem.DateTime,
        },
        default=construct.Struct(
            "unscaled_value"
            / construct.Switch(
                construct.this._.content_type,
                {
                    cosem.CommonDataTypes.double_long_unsigned: cosem.DoubleLongUnsigned,
                    cosem.CommonDataTypes.long: cosem.Long,
                    cosem.CommonDataTypes.long_unsigned: cosem.LongUnsigned,
                },
            ),
            "scaler_unit" / cosem.ScalerUnitField,
            "value"
            / construct.Computed(
                construct.this.unscaled_value * construct.this.scaler_unit.scaler.scale
            ),
        ),
    ),
)

NotificationBody: construct.Struct = construct.Struct(
    construct.Const(cosem.CommonDataTypes.array, cosem.CommonDataTypes),  # expect array
    "length" / construct.Int8ub,
    "list_items" / construct.Array(construct.this.length, Element),
)

LlcPdu: construct.Struct = cosem.get_llc_pdu_struct(NotificationBody)


def normalize_parsed_frame(
    frame: construct.Struct,
) -> Dict[str, Union[str, int, float, datetime]]:
    """Convert data from meters construct structure to a dictionary with common key names."""
    list_items = frame.information.notification_body.list_items

    dictionary: Dict[str, Union[str, int, float, datetime]] = {
        obis_map.NEK_HAN_FIELD_METER_MANUFACTURER: "Aidon"
    }
    for measure in list_items:
        element_name = obis_map.obis_name_map[measure.obis]

        if isinstance(measure.content, str):
            dictionary[element_name] = measure.content
        else:
            if hasattr(measure.content, "datetime"):
                dictionary[element_name] = measure.content.datetime
            else:
                dictionary[element_name] = (
                    measure.content.unscaled_value
                    if measure.content.unscaled_value == measure.content.value
                    else float(measure.content.value)
                )

    return dictionary


def decode_frame_content(
    frame_content: bytes,
) -> Dict[str, Union[str, int, float, datetime]]:
    """Decode meter LLC PDU frame content as a dictionary."""
    parsed = LlcPdu.parse(frame_content)
    return normalize_parsed_frame(parsed)
