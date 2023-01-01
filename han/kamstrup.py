"""Decoding support for Kamstrup meters."""
# pylint: disable=protected-access
from __future__ import annotations

from datetime import datetime

import construct  # type: ignore

from han import cosem, obis_map
from han.obis import Obis

Element: construct.Struct = construct.Struct(
    "_element_type" / construct.Peek(cosem.CommonDataTypes),
    "obis"
    / construct.If(
        cosem.CommonDataTypes.octet_string == construct.this._element_type,
        cosem.ObisCodeOctedStringField,
    ),
    "value_type" / construct.Peek(cosem.CommonDataTypes),
    "value"
    / construct.IfThenElse(
        cosem.CommonDataTypes.octet_string == construct.this.value_type,
        cosem.DateTimeField,
        cosem.Field,
    ),
    "_NullData" / cosem.NullData,  # trim null-data between elements
)

NotificationBody: construct.Struct = construct.Struct(
    construct.Const(
        cosem.CommonDataTypes.structure, cosem.CommonDataTypes
    ),  # expect structure
    "length" / construct.Int8ub,
    "list_items" / construct.GreedyRange(Element),
)

LlcPdu: construct.Struct = cosem.get_llc_pdu_struct(NotificationBody)

_field_scaling_standard = {
    "1.1.31.7.0.255": -2,  # IL1
    "1.1.51.7.0.255": -2,  # IL2
    "1.1.71.7.0.255": -2,  # IL3
    "1.1.1.8.0.255": 1,  # A14
    "1.1.2.8.0.255": 1,  # A23
    "1.1.3.8.0.255": 1,  # R12
    "1.1.4.8.0.255": 1,  # R34
}

_field_scaling_ct_meter = {
    "1.1.31.7.0.255": -3,  # IL1
    "1.1.51.7.0.255": -3,  # IL2
    "1.1.71.7.0.255": -3,  # IL3
    "1.1.1.8.0.255": 1,  # A14
    "1.1.2.8.0.255": 1,  # A23
    "1.1.3.8.0.255": 1,  # R12
    "1.1.4.8.0.255": 1,  # R34
}


def _normalize_parsed_items(
    list_items: construct.ListContainer,
) -> dict[str, str | int | float | datetime]:
    dictionary: dict[str, str | int | float | datetime] = {
        obis_map.FIELD_METER_MANUFACTURER: "Kamstrup",
    }

    meter_type = next((x for x in list_items if x.obis == "1.1.96.1.1.256"), None)
    is_ct_meter = meter_type is not None and meter_type.startswith("685")
    field_scaling = _field_scaling_ct_meter if is_ct_meter else _field_scaling_standard

    for measure in list_items:
        # list version is the only element without obis code
        element_name = (
            obis_map.obis_name_map[Obis.from_string(measure.obis).to_group_cdr_str()]
            if measure.obis
            else obis_map.FIELD_OBIS_LIST_VER_ID
        )

        if element_name == obis_map.FIELD_METER_DATETIME:
            dictionary[element_name] = measure.value.datetime
        else:
            if isinstance(measure.value, int):
                scale = field_scaling.get(measure.obis, None)
                if scale:
                    dictionary[element_name] = measure.value * (10**scale)
                else:
                    dictionary[element_name] = measure.value
            else:
                dictionary[element_name] = measure.value

    return dictionary


def normalize_parsed_frame(
    frame: construct.Struct,
) -> dict[str, str | int | float | datetime]:
    """Convert data from meters construct structure to a dictionary with common key names."""
    dictionary = _normalize_parsed_items(frame.information.notification_body.list_items)
    dictionary[obis_map.FIELD_METER_DATETIME] = frame.information.DateTime.datetime
    return dictionary


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
