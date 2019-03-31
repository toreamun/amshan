from decimal import *

import construct as c
import datetime

# See COSEM blue Book table 2 (Common data types) in section 4.1.5 Common data types
# NOTE: Not all types are defined here
CosemCommonDataTypes = c.Enum(
    c.Byte,
    null_data=0,
    array=1,
    structure=2,
    double_long_unsigned=6,  # Unsigned32 [0...4 294 967 295]
    octet_string=9,  # An ordered sequence of octets (8 bit bytes)
    visible_string=10,  # An ordered sequence of ASCII characters
    integer=15,  # Integer8 [-128...127]
    long=16,  # Integer16 [-32 768...32 767]
    long_unsigned=18,  # Unsigned16 [0...65 535]
    enum=22  # as CosemPhysicalUnits
)

# See COSEM blue Book table 4 (Enumerated values for physical units) in section 4.3.2 Register
# NOTE: Not all values are defined here
CosemPhysicalUnits = c.Enum(c.Byte, W=27, var=29, A=33, V=35)

ObisCode = c.ExprAdapter(
    c.Byte[6],
    decoder=lambda obj, ctx: ".".join("%d" % b for b in obj),
    encoder=lambda obj, ctx: [int(part) for part in obj.split(".")],
)

ObisOctedStringField = c.FocusedSeq(
    "code",
    c.Const(CosemCommonDataTypes.octet_string, CosemCommonDataTypes),  # expect octet string (bytes)
    c.Const(6, c.Byte),  # expect length 6
    "code" / ObisCode
)

CosemIntegerField = c.FocusedSeq(
    "value",
    c.Const(CosemCommonDataTypes.integer, CosemCommonDataTypes),  # expect integer
    "value" / c.Int8sb
)

CosemUnitField = c.FocusedSeq(
    "value",
    c.Const(CosemCommonDataTypes.enum, CosemCommonDataTypes),  # expect enum
    "value" / CosemPhysicalUnits
)

CosemScaler = c.Struct(
    "exponent" / CosemIntegerField,  # This is the exponent (to the base of 10) of the multiplication factor.
    "scale" / c.Computed(lambda ctx: Decimal(10) ** ctx.exponent)
)

CosemScalerUnit = c.Struct(
    c.Const(CosemCommonDataTypes.structure, CosemCommonDataTypes),  # expect structure
    c.Const(2, c.Byte),  # expect length 2
    "scaler" / CosemScaler,
    "unit" / CosemUnitField
)

OptionalDateTimeByte = c.ExprAdapter(
    c.Byte,
    decoder=lambda obj, ctx: obj if obj != 0xff else None,
    encoder=lambda obj, ctx: obj if obj is not None else 0xff,
)

ClockStatus = c.BitStruct(
    "invalid_value" / c.BitsInteger(1),
    "doubtful_value" / c.BitsInteger(1),
    "different_clock_base" / c.BitsInteger(1),
    "invalid_clock_status" / c.BitsInteger(1),
    c.BitsInteger(3),
    "daylight_saving_active" / c.BitsInteger(1),
)

ObisDateTime = c.Struct(
        "item_length" / c.Byte,
        "year" / c.Int16ub,
        "month" / c.Byte,
        "day_of_month" / c.Byte,
        "day_of_week" / c.Byte,
        "hour" / OptionalDateTimeByte,
        "minute" / OptionalDateTimeByte,
        "second" / OptionalDateTimeByte,
        "hundredths_of_second" / OptionalDateTimeByte,
        "deviation" / c.ExprAdapter(
            c.Int16sb,
            decoder=lambda obj, ctx: obj if obj != -0x8000 else None,
            encoder=lambda obj, ctx: obj if obj is not None else -0x8000,
        ),
        "clock_status_byte" / c.Peek(OptionalDateTimeByte),
        "clock_status" / c.If(
            0xff != c.this.clock_status_byte,
            c.BitStruct(
                "invalid_value" / c.BitsInteger(1),
                "doubtful_value" / c.BitsInteger(1),
                "different_clock_base" / c.BitsInteger(1),
                "invalid_clock_status" / c.BitsInteger(1),
                c.BitsInteger(3),
                "daylight_saving_active" / c.BitsInteger(1)
            ),
        ),
        c.If(0xff == c.this.clock_status_byte, c.Byte),
        "datetime" / c.Computed(lambda ctx: datetime.datetime(
            ctx.year, ctx.month, ctx.day_of_month,
            ctx.hour, ctx.minute, ctx.second,
            ctx.hundredths_of_second * 10000 if ctx.hundredths_of_second is not None else 0,
            datetime.timezone(datetime.timedelta(minutes=ctx.deviation)) if ctx.deviation is not None else None
        ))
    )

OptionalDateTime = c.Struct(
    "content_type" / CosemCommonDataTypes,
    "value" / c.If(
        c.this.content_type == CosemCommonDataTypes.octet_string,
        ObisDateTime
    )
)

Element = c.Struct(
    c.Const(CosemCommonDataTypes.structure, CosemCommonDataTypes),  # expect structure
    "length" / c.Byte,
    "obis" / ObisOctedStringField,
    "content_type" / CosemCommonDataTypes,
    "content" / c.IfThenElse(
        c.this.content_type == CosemCommonDataTypes.visible_string,
        c.PascalString(c.Byte, "ASCII"),
        c.Embedded(
            c.Struct(
                "unscaled_value" / c.Switch(
                    c.this._.content_type,
                    {
                        CosemCommonDataTypes.double_long_unsigned: c.Int32ub,
                        CosemCommonDataTypes.long: c.Int16sb,
                        CosemCommonDataTypes.long_unsigned: c.Int16ub
                    }),
                c.Embedded(CosemScalerUnit),
                "value" / c.Computed(c.this.unscaled_value * c.this.scaler.scale)
            )
        ))
)

NotificationBody = c.Struct(
    c.Const(CosemCommonDataTypes.array, CosemCommonDataTypes),  # expect array
    "list_count" / c.Byte,
    "list_items" / c.RepeatUntil(
        lambda obj, lst, ctx: len(lst) == ctx.list_count,
        Element)
)

LongInvokeIdAndPriority = c.BitStruct(
    "invoke-id" / c.BitsInteger(24),
    c.Padding(4),
    "self-descriptive" / c.Enum(c.BitsInteger(1), NotSelfDescriptive=0, SelfDescriptive=1),
    "processing-option" / c.Enum(c.BitsInteger(1), ContinueOnError=0, BreakOnError=1),
    "service-class" / c.Enum(c.BitsInteger(1), Unconfirmed=0, Confirmed=1),
    "priority" / c.Enum(c.BitsInteger(1), Normal=0, High=1)
)

Apdpu = c.Struct(
    "Tag" / c.Byte,
    "LongInvokeIdAndPriority" / LongInvokeIdAndPriority,
    "DateTime" / OptionalDateTime,
    "notification-body" / NotificationBody
)

LlcPdu = c.Struct(
    "dsap" / c.Byte,
    "ssap" / c.Byte,
    "control" / c.Byte,
    "information" / Apdpu
)

m34 = 'e6e700' \
      '0f400000' \
      '00' \
      '090c07e3020401173416ff800000' \
      '0201' \
      '06000016dc'

# m34 = e6e700 0f 40000000 090c07e3020401173416ff800000 020106000016dc
# U516 e6e700 0f 40000000 00                           0101 0203 0906 0100010700ff 06 00000635 0202 0f00 161b
u516L1 = 'e6e7000f40000000000101020309060100010700ff060000063502020f00161b'
# u516L2 = 'e6e7000f4000000000010c020209060101000281ff0a0b4149444f4e5f5630303031020209060000600100ff0a1037333539393932383932353837363635020209060000600107ff0a0436353235020309060100010700ff06000000ed02020f00161b020309060100020700ff060000000002020f00161b020309060100030700ff060000000002020f00161d020309060100040700ff060000007f02020f00161d0203090601001f0700ff10000c02020fff1621020309060100470700ff10000702020fff1621020309060100200700ff1208ef02020fff1623020309060100340700ff12091302020fff1623020309060100480700ff12092c02020fff1623'
u516L2 = 'e6e7000f40000000090c07e3020401173416ff003c00010c020209060101000281ff0a0b4149444f4e5f5630303031020209060000600100ff0a1037333539393932383932353837363635020209060000600107ff0a0436353235020309060100010700ff06000000ed02020f00161b020309060100020700ff060000000002020f00161b020309060100030700ff060000000002020f00161d020309060100040700ff060000007f02020f00161d0203090601001f0700ff10000c02020fff1621020309060100470700ff10000702020fff1621020309060100200700ff1208ef02020fff1623020309060100340700ff12091302020fff1623020309060100480700ff12092c02020fff1623'

m34b = bytes.fromhex(m34)
u516b = bytes.fromhex(u516L2)

# f = open('output', 'wb')
# f.write(u516b)
# msg = LlcPdu.parse(m34b)
# print(msg)

msg = LlcPdu.parse(u516b)
print(msg)
