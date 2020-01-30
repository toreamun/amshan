import construct

from readams.meterdecode import cosem

KaifaNotificationBody = construct.Struct(
    construct.Const(cosem.CommonDataTypes.structure, cosem.CommonDataTypes),  # expect structure
    "length" / construct.Int8ub,
    "list_items" / construct.Array(construct.this.length, construct.Struct(
        "index" / construct.Computed(construct.this._index),
        "_value_type" / cosem.CommonDataTypes,
        "value" / construct.Switch(
            construct.this._value_type,
            {
                # octed string is used for both text and date time
                cosem.CommonDataTypes.octet_string: construct.IfThenElse(
                    construct.this._index < 4,
                    cosem.OctedStringText,
                    cosem.DateTime),
                cosem.CommonDataTypes.double_long_unsigned: cosem.DoubleLongUnsigned
            })
    ))
)

# KaifaList1 = c.Struct(
#     NEK_HAN_FIELD_ACTIVE_POWER_IMPORT / scaled_simple_value(cosem.CosemPhysicalUnits.W, 0)
# )
#
#
# def kaifa_list_2(is_three_phase: bool):
#     return c.Struct(
#         NEK_HAN_FIELD_OBIS_LIST_VER_ID / cosem.CosemOctedStringTextField,
#         NEK_HAN_FIELD_METER_ID / cosem.CosemOctedStringTextField,
#         NEK_HAN_FIELD_METER_TYPE / cosem.CosemOctedStringTextField,
#
#         NEK_HAN_FIELD_ACTIVE_POWER_IMPORT / scaled_simple_value(cosem.CosemPhysicalUnits.W, 0),
#         NEK_HAN_FIELD_ACTIVE_POWER_EXPORT / scaled_simple_value(cosem.CosemPhysicalUnits.W, 0),
#
#         NEK_HAN_FIELD_REACTIVE_POWER_IMPORT / scaled_simple_value(cosem.CosemPhysicalUnits.var, 0),
#         NEK_HAN_FIELD_REACTIVE_POWER_EXPORT / scaled_simple_value(cosem.CosemPhysicalUnits.var, 0),
#
#         NEK_HAN_FIELD_CURRENT_L1 / scaled_simple_value(cosem.CosemPhysicalUnits.A, -3),
#         c.If(is_three_phase, NEK_HAN_FIELD_CURRENT_L2 / scaled_simple_value(cosem.CosemPhysicalUnits.A, -3)),
#         c.If(is_three_phase, NEK_HAN_FIELD_CURRENT_L3 / scaled_simple_value(cosem.CosemPhysicalUnits.A, -3)),
#
#         NEK_HAN_FIELD_VOLTAGE_L1 / scaled_simple_value(cosem.CosemPhysicalUnits.V, -1),
#         c.If(is_three_phase, NEK_HAN_FIELD_VOLTAGE_L2 / scaled_simple_value(cosem.CosemPhysicalUnits.V, -1)),
#         c.If(is_three_phase, NEK_HAN_FIELD_VOLTAGE_L3 / scaled_simple_value(cosem.CosemPhysicalUnits.V, -1))
#     )
#
#
# def kaifa_list_3(is_three_phase: bool):
#     return c.Struct(
#         NEK_HAN_FIELD_OBIS_LIST_VER_ID / cosem.CosemOctedStringTextField,
#         NEK_HAN_FIELD_METER_ID / cosem.CosemOctedStringTextField,
#         NEK_HAN_FIELD_METER_TYPE / cosem.CosemOctedStringTextField,
#
#         NEK_HAN_FIELD_ACTIVE_POWER_IMPORT / scaled_simple_value(cosem.CosemPhysicalUnits.W, 0),
#         NEK_HAN_FIELD_ACTIVE_POWER_EXPORT / scaled_simple_value(cosem.CosemPhysicalUnits.W, 0),
#
#         NEK_HAN_FIELD_REACTIVE_POWER_IMPORT / scaled_simple_value(cosem.CosemPhysicalUnits.var, 0),
#         NEK_HAN_FIELD_REACTIVE_POWER_EXPORT / scaled_simple_value(cosem.CosemPhysicalUnits.var, 0),
#
#         NEK_HAN_FIELD_CURRENT_L1 / scaled_simple_value(cosem.CosemPhysicalUnits.A, -3),
#         c.If(is_three_phase, NEK_HAN_FIELD_CURRENT_L2 / scaled_simple_value(cosem.CosemPhysicalUnits.A, -3)),
#         c.If(is_three_phase, NEK_HAN_FIELD_CURRENT_L3 / scaled_simple_value(cosem.CosemPhysicalUnits.A, -3)),
#
#         NEK_HAN_FIELD_VOLTAGE_L1 / scaled_simple_value(cosem.CosemPhysicalUnits.V, -1),
#         c.If(is_three_phase, NEK_HAN_FIELD_VOLTAGE_L2 / scaled_simple_value(cosem.CosemPhysicalUnits.V, -1)),
#         c.If(is_three_phase, NEK_HAN_FIELD_VOLTAGE_L3 / scaled_simple_value(cosem.CosemPhysicalUnits.V, -1)),
#
#         NEK_HAN_FIELD_METER_DATETIME / cosem.CosemDateTimeField,
#
#         NEK_HAN_FIELD_ACTIVE_POWER_IMPORT_HOUR / scaled_simple_value(cosem.CosemPhysicalUnits.Wh, 0),
#         NEK_HAN_FIELD_ACTIVE_POWER_EXPORT_HOUR / scaled_simple_value(cosem.CosemPhysicalUnits.Wh, 0),
#
#         NEK_HAN_FIELD_REACTIVE_POWER_IMPORT_HOUR / scaled_simple_value(cosem.CosemPhysicalUnits.varh, 0),
#         NEK_HAN_FIELD_REACTIVE_POWER_EXPORT_HOUR / scaled_simple_value(cosem.CosemPhysicalUnits.varh, 0)
#     )


# KaifaList2SinglePhase = kaifa_list_2(is_three_phase=False)
# KaifaList2ThreePhase = kaifa_list_2(is_three_phase=True)
# KaifaList3SinglePhase = kaifa_list_3(is_three_phase=False)
# KaifaList3ThreePhase = kaifa_list_3(is_three_phase=True)

# KaifaNotificationBody = c.Struct(
#     c.Const(cosem.CosemCommonDataTypes.structure, cosem.CosemCommonDataTypes),  # expect structure
#     "length" / c.Int8ub,
#     "data" / c.Switch(c.this.length, {
#         1: KaifaList1,
#         9: KaifaList2SinglePhase,
#         13: KaifaList2ThreePhase,
#         14: KaifaList3SinglePhase,
#         18: KaifaList3ThreePhase,
#     })
# )

LlcPdu = cosem.get_llc_pdu_struct(KaifaNotificationBody)


def measure_to_dic(measure):
    return {
        "value": int(measure.scaled_value) if measure.scale == 1 else float(measure.scaled_value),
        "unit": measure.unit
    }


def kaifa_message_to_dictionary(kaifa_message: construct.Container) -> dict:
    data = kaifa_message.information.notification_body.data
    dictionary = {cosem.NEK_HAN_FIELD_METER_DATETIME: kaifaMsg2.information.DateTime.datetime.isoformat()}

    for key in data():
        if not key.startswith("_"):
            value = data[key]
            if isinstance(value, str):
                dictionary[key] = value
            else:
                if key == cosem.NEK_HAN_FIELD_METER_DATETIME:
                    dictionary[key]: value.datetime.isoformat()
                else:
                    dictionary[key] = measure_to_dic(value)

    return dictionary
