import construct

from meterdecode import obis_map, cosem

KamstrupElement = construct.Struct(
    "_element_type" / construct.Peek(cosem.CommonDataTypes),
    "obis" / construct.If(cosem.CommonDataTypes.octet_string == construct.this._element_type,
                          cosem.ObisCodeOctedStringField),
    "value_type" / construct.Peek(cosem.CommonDataTypes),
    "value" / construct.IfThenElse(cosem.CommonDataTypes.octet_string == construct.this.value_type, cosem.DateTimeField,
                                   cosem.Field),
)

KamtrupNotificationBody = construct.Struct(
    construct.Const(cosem.CommonDataTypes.structure, cosem.CommonDataTypes),  # expect structure
    "length" / construct.Int8ub,
    "list_items" / construct.GreedyRange(KamstrupElement)
)

LlcPdu = cosem.get_llc_pdu_struct(KamtrupNotificationBody)


def normalize_llcpdu_frame_content(frame: LlcPdu) -> dict:
    field_scaling = {
        "1.1.31.7.0.255": -2,
        "1.1.51.7.0.255": -2,
        "1.1.71.7.0.255": -2,
    }

    list_items = frame.information.notification_body.list_items
    dictionary = {obis_map.NEK_HAN_FIELD_METER_DATETIME: frame.information.DateTime.datetime}

    for measure in list_items:
        # list version is the only element without obis code
        element_name = obis_map.obis_name_map[measure.obis] if measure.obis else obis_map.NEK_HAN_FIELD_OBIS_LIST_VER_ID

        if element_name == obis_map.NEK_HAN_FIELD_METER_DATETIME:
            dictionary[element_name] = measure.value.datetime
        else:
            if isinstance(measure.value, int):
                scale = field_scaling.get(measure.obis, None)
                if scale:
                    dictionary[element_name] = measure.value * (10 ** scale)
                else:
                    dictionary[element_name] = measure.value
            else:
                dictionary[element_name] = measure.value

    return dictionary


def decode_frame(frame: bytes) -> dict:
    parsed = LlcPdu.parse(frame)
    return normalize_llcpdu_frame_content(parsed)
