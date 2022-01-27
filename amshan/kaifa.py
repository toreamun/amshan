"""Decoding support for Kaifa meters."""
# pylint: disable=protected-access
from __future__ import annotations

from datetime import datetime
from enum import Enum

import construct  # type: ignore
from amshan import cosem, obis_map
from amshan.obis import Obis


class KaifaBodyType(Enum):
    """Kaifa body structure type."""

    VALUE_ELEMENTS = "value_elements"
    OBIS_ELEMENTS = "obis_elements"


Element: construct.Struct = construct.Struct(
    "_element_type" / construct.Peek(cosem.CommonDataTypes),
    "obis" / cosem.ObisCodeOctedStringField,
    "value_type" / construct.Peek(cosem.CommonDataTypes),
    "value" / cosem.Field,
)


NotificationBodyValueElements: construct.Struct = construct.Struct(
    construct.Const(
        cosem.CommonDataTypes.structure, cosem.CommonDataTypes
    ),  # expect structure
    "length" / construct.Int8ub,
    "list_items"
    / construct.Array(
        construct.this.length,
        construct.Struct(
            "index" / construct.Computed(construct.this._index),
            "value" / cosem.Field,
        ),
    ),
    "_length_check"
    / construct.Check(
        construct.this.length == construct.len_(construct.this.list_items)
    ),
    "type" / construct.Computed(lambda _: KaifaBodyType.VALUE_ELEMENTS),
)

NotificationBodyObisElements: construct.Struct = construct.Struct(
    construct.Const(
        cosem.CommonDataTypes.structure, cosem.CommonDataTypes
    ),  # expect structure
    "_fields" / construct.Int8ub,
    "length" / construct.Computed(lambda ctx: int(ctx._fields / 2)),
    "list_items" / construct.GreedyRange(Element),
    "_length_check"
    / construct.Check(lambda ctx: (ctx._fields / 2) == len(ctx.list_items)),
    "type" / construct.Computed(lambda _: KaifaBodyType.OBIS_ELEMENTS),
)

LlcPduNotificationBodyObisElements = cosem.get_llc_pdu_struct(
    NotificationBodyObisElements
)

LlcPduNotificationBodyValueElements = cosem.get_llc_pdu_struct(
    NotificationBodyValueElements
)

LlcPdu: construct.Struct = construct.Select(
    LlcPduNotificationBodyObisElements, LlcPduNotificationBodyValueElements
)


def _get_field_lists() -> list[list[str]]:
    item_order_list_3_three_phase = [
        obis_map.FIELD_OBIS_LIST_VER_ID,
        obis_map.FIELD_METER_ID,
        obis_map.FIELD_METER_TYPE,
        obis_map.FIELD_ACTIVE_POWER_IMPORT,
        obis_map.FIELD_ACTIVE_POWER_EXPORT,
        obis_map.FIELD_REACTIVE_POWER_IMPORT,
        obis_map.FIELD_REACTIVE_POWER_EXPORT,
        obis_map.FIELD_CURRENT_L1,
        obis_map.FIELD_CURRENT_L2,
        obis_map.FIELD_CURRENT_L3,
        obis_map.FIELD_VOLTAGE_L1,
        obis_map.FIELD_VOLTAGE_L2,
        obis_map.FIELD_VOLTAGE_L3,
        obis_map.FIELD_METER_DATETIME,
        obis_map.FIELD_ACTIVE_POWER_IMPORT_TOTAL,
        obis_map.FIELD_ACTIVE_POWER_EXPORT_TOTAL,
        obis_map.FIELD_REACTIVE_POWER_IMPORT_TOTAL,
        obis_map.FIELD_REACTIVE_POWER_EXPORT_TOTAL,
    ]

    item_order_list_3_single_phase = (
        item_order_list_3_three_phase[:8]
        + item_order_list_3_three_phase[10:11]
        + item_order_list_3_three_phase[13:]
    )

    item_order_list_2_single_phase = item_order_list_3_single_phase[:-5]

    item_order_list_2_three_phase = item_order_list_3_three_phase[:-5]

    return [
        [obis_map.FIELD_ACTIVE_POWER_IMPORT],
        item_order_list_2_single_phase,
        item_order_list_2_three_phase,
        item_order_list_3_single_phase,
        item_order_list_3_three_phase,
    ]


_field_order_lists: list[list[str]] = _get_field_lists()

_FIELD_SCALING = {
    obis_map.FIELD_CURRENT_L1: -3,
    obis_map.FIELD_CURRENT_L2: -3,
    obis_map.FIELD_CURRENT_L3: -3,
    obis_map.FIELD_VOLTAGE_L1: -1,
    obis_map.FIELD_VOLTAGE_L2: -1,
    obis_map.FIELD_VOLTAGE_L3: -1,
}


def _normalize_parsed_value_elements_frame(
    frame: construct.Struct,
) -> dict[str, str | int | float | datetime]:
    list_items = frame.information.notification_body.list_items
    current_list_names: list[str] = next(
        (x for x in _field_order_lists if len(x) == len(list_items)), []
    )

    dictionary: dict[str, str | int | float | datetime] = {
        obis_map.FIELD_METER_MANUFACTURER: "Kaifa",
        obis_map.FIELD_METER_DATETIME: frame.information.DateTime.datetime,
    }

    for measure in list_items:
        element_name = current_list_names[measure.index]

        if element_name == obis_map.FIELD_METER_DATETIME:
            dictionary[element_name] = measure.value.datetime
        else:
            scale = _FIELD_SCALING.get(element_name, None)
            if scale:
                scaled_value = round(measure.value * (10 ** scale), abs(scale))
                dictionary[element_name] = scaled_value
            else:
                dictionary[element_name] = measure.value

    return dictionary


def _normalize_parsed_obis_elements_frame(
    frame: construct.Struct,
) -> dict[str, str | int | float | datetime]:
    dictionary: dict[str, str | int | float | datetime] = {
        obis_map.FIELD_METER_MANUFACTURER: "Kaifa",
    }

    list_items = frame.information.notification_body.list_items
    for measure in list_items:
        obis_group_cdr = Obis.from_string(measure.obis).to_group_cdr_str()
        if obis_group_cdr in obis_map.obis_name_map:
            element_name = obis_map.obis_name_map[obis_group_cdr]
        else:
            element_name = obis_group_cdr

        if hasattr(measure.value, "datetime"):
            dictionary[element_name] = measure.value.datetime
        else:
            scale = _FIELD_SCALING.get(element_name, None)
            if scale:
                scaled_value = round(measure.value * (10 ** scale), abs(scale))
                dictionary[element_name] = scaled_value
            else:
                dictionary[element_name] = measure.value

    return dictionary


def normalize_parsed_frame(
    frame: construct.Struct,
) -> dict[str, str | int | float | datetime]:
    """Convert data from meters construct structure to a dictionary with common key names."""
    list_type = frame.information.notification_body.type
    if list_type == KaifaBodyType.VALUE_ELEMENTS:
        return _normalize_parsed_value_elements_frame(frame)

    if list_type == KaifaBodyType.OBIS_ELEMENTS:
        return _normalize_parsed_obis_elements_frame(frame)

    raise ValueError(f"Unexpected list type {list_type}")


def decode_frame_content(
    frame_content: bytes,
) -> dict[str, str | int | float | datetime]:
    """Decode meter LLC PDU frame content as a dictionary."""
    parsed = LlcPdu.parse(frame_content)
    return normalize_parsed_frame(parsed)
