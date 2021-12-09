"""Decoding support for Kaifa meters."""
# pylint: disable=protected-access
from datetime import datetime
from typing import Dict, List, Union

import construct  # type: ignore

from amshan import cosem, obis_map

NotificationBody: construct.Struct = construct.Struct(
    construct.Const(
        cosem.CommonDataTypes.structure, cosem.CommonDataTypes
    ),  # expect structure
    "length" / construct.Int8ub,
    "list_items"
    / construct.Array(
        construct.this.length,
        construct.Struct(
            "index" / construct.Computed(construct.this._index),
            "_value_type" / cosem.CommonDataTypes,
            "value"
            / construct.Switch(
                construct.this._value_type,
                {
                    # octed string is used for both text and date time
                    cosem.CommonDataTypes.octet_string: construct.IfThenElse(
                        construct.this._index < 4, cosem.OctedStringText, cosem.DateTime
                    ),
                    cosem.CommonDataTypes.double_long_unsigned: cosem.DoubleLongUnsigned,
                },
            ),
        ),
    ),
)

LlcPdu: construct.Struct = cosem.get_llc_pdu_struct(NotificationBody)


def _get_field_lists() -> List[List[str]]:
    item_order_list_3_three_phase = [
        obis_map.NEK_HAN_FIELD_OBIS_LIST_VER_ID,
        obis_map.NEK_HAN_FIELD_METER_ID,
        obis_map.NEK_HAN_FIELD_METER_TYPE,
        obis_map.NEK_HAN_FIELD_ACTIVE_POWER_IMPORT,
        obis_map.NEK_HAN_FIELD_ACTIVE_POWER_EXPORT,
        obis_map.NEK_HAN_FIELD_REACTIVE_POWER_IMPORT,
        obis_map.NEK_HAN_FIELD_REACTIVE_POWER_EXPORT,
        obis_map.NEK_HAN_FIELD_CURRENT_L1,
        obis_map.NEK_HAN_FIELD_CURRENT_L2,
        obis_map.NEK_HAN_FIELD_CURRENT_L3,
        obis_map.NEK_HAN_FIELD_VOLTAGE_L1,
        obis_map.NEK_HAN_FIELD_VOLTAGE_L2,
        obis_map.NEK_HAN_FIELD_VOLTAGE_L3,
        obis_map.NEK_HAN_FIELD_METER_DATETIME,
        obis_map.NEK_HAN_FIELD_ACTIVE_POWER_IMPORT_HOUR,
        obis_map.NEK_HAN_FIELD_ACTIVE_POWER_EXPORT_HOUR,
        obis_map.NEK_HAN_FIELD_REACTIVE_POWER_IMPORT_HOUR,
        obis_map.NEK_HAN_FIELD_REACTIVE_POWER_EXPORT_HOUR,
    ]

    item_order_list_3_single_phase = (
        item_order_list_3_three_phase[:8]
        + item_order_list_3_three_phase[10:11]
        + item_order_list_3_three_phase[13:]
    )

    item_order_list_2_single_phase = item_order_list_3_single_phase[:-5]

    item_order_list_2_three_phase = item_order_list_3_three_phase[:-5]

    return [
        [obis_map.NEK_HAN_FIELD_ACTIVE_POWER_IMPORT],
        item_order_list_2_single_phase,
        item_order_list_2_three_phase,
        item_order_list_3_single_phase,
        item_order_list_3_three_phase,
    ]


_field_order_lists: List[List[str]] = _get_field_lists()

_FIELD_SCALING = {
    obis_map.NEK_HAN_FIELD_CURRENT_L1: -3,
    obis_map.NEK_HAN_FIELD_CURRENT_L2: -3,
    obis_map.NEK_HAN_FIELD_CURRENT_L3: -3,
    obis_map.NEK_HAN_FIELD_VOLTAGE_L1: -1,
    obis_map.NEK_HAN_FIELD_VOLTAGE_L2: -1,
    obis_map.NEK_HAN_FIELD_VOLTAGE_L3: -1,
}


def normalize_parsed_frame(
    frame: construct.Struct,
) -> Dict[str, Union[str, int, float, datetime]]:
    """Convert data from meters construct structure to a dictionary with common key names."""
    list_items = frame.information.notification_body.list_items

    current_list_names: List[str] = next(
        (x for x in _field_order_lists if len(x) == len(list_items)), []
    )

    dictionary = {
        obis_map.NEK_HAN_FIELD_METER_MANUFACTURER: "Kaifa",
        obis_map.NEK_HAN_FIELD_METER_DATETIME: frame.information.DateTime.datetime,
    }

    for measure in list_items:
        element_name = current_list_names[measure.index]

        if element_name == obis_map.NEK_HAN_FIELD_METER_DATETIME:
            dictionary[element_name] = measure.value.datetime
        else:
            scale = _FIELD_SCALING.get(element_name, None)
            if scale:
                scaled_value = measure.value * (10 ** scale)
                dictionary[element_name] = scaled_value
            else:
                dictionary[element_name] = measure.value

    return dictionary


def decode_frame_content(
    frame_content: bytes,
) -> Dict[str, Union[str, int, float, datetime]]:
    """Decode meter LLC PDU frame content as a dictionary."""
    parsed = LlcPdu.parse(frame_content)
    return normalize_parsed_frame(parsed)
