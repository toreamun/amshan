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
CosemPhysicalUnits = c.Enum(c.Byte, W=27, var=29, Wh=30, varh=32, A=33, V=35)

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

# See COSEM blue Book section 4.1.6.1 Date and time formats
CosemDateTime = c.Struct(
    c.Const(0x0c, c.Byte),  # expect length 12
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

OptionalDateTime = c.FocusedSeq(
    "value",
    "content_type" / CosemCommonDataTypes,
    c.Check(lambda ctx:
            ctx.content_type == CosemCommonDataTypes.null_data
            or ctx.content_type == CosemCommonDataTypes.octet_string),
    "value" / c.If(
        c.this.content_type != CosemCommonDataTypes.null_data,
        CosemDateTime
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
        c.IfThenElse(
            c.this.content_type == CosemCommonDataTypes.octet_string,
            "datetime" / CosemDateTime,
            c.Struct(
                "unscaled_value" / c.Switch(
                    c.this._.content_type,
                    {
                        CosemCommonDataTypes.double_long_unsigned: c.Int32ub,
                        CosemCommonDataTypes.long: c.Int16sb,
                        CosemCommonDataTypes.long_unsigned: c.Int16ub
                    }),
                "scaler_unit" / CosemScalerUnit,
                "value" / c.Computed(c.this.unscaled_value * c.this.scaler_unit.scaler.scale)
            )
        )
    )
)

NotificationBody = c.Struct(
    c.Const(CosemCommonDataTypes.array, CosemCommonDataTypes),  # expect array
    "list_count" / c.Byte,
    "list_items" / c.RepeatUntil(
        lambda obj, lst, ctx: len(lst) == ctx.list_count,
        Element),
)

NotificationBody2 = c.Struct(
        Element
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
