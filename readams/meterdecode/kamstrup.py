import construct

from readams.meterdecode import cosem

KamstrupElement = construct.Struct(
    "_element_type" / construct.Peek(cosem.CommonDataTypes),
    "obis" / construct.If(cosem.CommonDataTypes.octet_string == construct.this._element_type, cosem.ObisCodeOctedStringField),
    "value_type" / construct.Peek(cosem.CommonDataTypes),
    "value" / construct.IfThenElse(cosem.CommonDataTypes.octet_string == construct.this.value_type, cosem.DateTimeField, cosem.Field),
)

KamtrupNotificationBody = construct.Struct(
    construct.Const(cosem.CommonDataTypes.structure, cosem.CommonDataTypes),  # expect structure
    "length" / construct.Int8ub,
    "list_items" / construct.GreedyRange(KamstrupElement)
)

LlcPdu = cosem.get_llc_pdu_struct(KamtrupNotificationBody)
