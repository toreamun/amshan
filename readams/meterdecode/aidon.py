import construct

from readams.meterdecode import cosem

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
