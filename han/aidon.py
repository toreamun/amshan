"""Decoding support for Aidon meters."""
from __future__ import annotations

from datetime import datetime

import construct  # type: ignore

from han import cosem, obis_map
from han.obis import Obis

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


def _normalize_parsed_items(
    list_items: construct.ListContainer,
) -> dict[str, str | int | float | datetime]:
    dictionary: dict[str, str | int | float | datetime] = {
        obis_map.FIELD_METER_MANUFACTURER: "Aidon"
    }
    for measure in list_items:
        obis_group_cdr = Obis.from_string(measure.obis).to_group_cdr_str()
        if obis_group_cdr in obis_map.obis_name_map:
            element_name = obis_map.obis_name_map[obis_group_cdr]
        else:
            element_name = obis_group_cdr

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


def normalize_parsed_frame(
    frame: construct.Struct,
) -> dict[str, str | int | float | datetime]:
    """Convert data from meters construct structure to a dictionary with common key names."""
    return _normalize_parsed_items(frame.information.notification_body.list_items)


def normalize_parsed_notification(
    notification: construct.Struct,
) -> dict[str, str | int | float | datetime]:
    """Convert data from meters construct structure to a dictionary with common key names."""
    return _normalize_parsed_items(notification.list_items)


def decode_frame_content(
    frame_content: bytes,
) -> dict[str, str | int | float | datetime]:
    """Decode meter LLC PDU frame content as a dictionary."""
    parsed = LlcPdu.parse(frame_content)
    return normalize_parsed_frame(parsed)


def decode_notification_body(
    notification_body: bytes,
) -> dict[str, str | int | float | datetime]:
    """Decode meter APDU notification body as a dictionary."""
    parsed = NotificationBody.parse(notification_body)
    return normalize_parsed_notification(parsed)
