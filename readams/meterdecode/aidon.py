import construct
from readams.meterdecode import cosem, obis_map

AidonElement = construct.Struct(
    construct.Const(cosem.CommonDataTypes.structure, cosem.CommonDataTypes),  # expect structure
    "length" / construct.Int8ub,
    "obis" / cosem.ObisCodeOctedStringField,
    "content_type" / cosem.CommonDataTypes,
    "content" / construct.Switch(
        construct.this.content_type,
        {
            cosem.CommonDataTypes.visible_string: cosem.VisibleString,
            cosem.CommonDataTypes.octet_string: cosem.DateTime,
        },
        default=construct.Struct(
            "unscaled_value" / construct.Switch(
                construct.this._.content_type,
                {
                    cosem.CommonDataTypes.double_long_unsigned: cosem.DoubleLongUnsigned,
                    cosem.CommonDataTypes.long: cosem.Long,
                    cosem.CommonDataTypes.long_unsigned: cosem.LongUnsigned
                }),
            "scaler_unit" / cosem.ScalerUnitField,
            "value" / construct.Computed(construct.this.unscaled_value * construct.this.scaler_unit.scaler.scale)
        )
    )
)

AidonNotificationBody = construct.Struct(
    construct.Const(cosem.CommonDataTypes.array, cosem.CommonDataTypes),  # expect array
    "length" / construct.Int8ub,
    "list_items" / construct.Array(construct.this.length, AidonElement)
)

LlcPdu = cosem.get_llc_pdu_struct(AidonNotificationBody)


def normalize_llcpdu_frame_content(frame: LlcPdu) -> dict:
    list_items = frame.information.notification_body.list_items

    dictionary = {}
    for measure in list_items:
        element_name = obis_map.obis_name_map[measure.obis]

        if isinstance(measure.content, str):
            dictionary[element_name] = measure.content
        else:
            if hasattr(measure.content, "datetime"):
                dictionary[element_name] = measure.content.datetime
            else:
                dictionary[element_name] = (measure.content.unscaled_value
                                            if measure.content.unscaled_value == measure.content.value
                                            else float(measure.content.value))

    return dictionary


def decode_frame(frame: bytes) -> dict:
    parsed = LlcPdu.parse(frame)
    return normalize_llcpdu_frame_content(parsed)
