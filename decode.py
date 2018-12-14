import json
import pathlib
import construct as c
import datetime

FrameInfo = c.BitStruct(
    "frame_format" / c.Bit[4],
    "separator" / c.Bit,
    "frame_length" / c.BitsInteger(11),
)

Header = c.Struct(
    "frame_info" / FrameInfo,
    "dest_addr" / c.Int8ub,  # TODO: Proper parsing. Not static.
    "src_addr" / c.Struct(  # TODO: Proper parsing. Not static.
        c.Int8ub,
        c.Int8ub,
    ),
    "control_field" / c.Byte,
    "hcs" / c.Bytes(2),  # TODO: Verify checksum
)

Footer = c.Struct(
    "fcs" / c.Bytes(2),  # TODO: Verify checksum
)


# ########################
#  Data types
# ########################
Timestamp = c.Struct(
    "item_type" / c.Const(b'\x09'),
    "item_length" / c.Int8ub,
    "year" / c.Int16ub,
    "month" / c.Int8ub,
    "day" / c.Int8ub,
    c.Byte,
    "hour" / c.Int8ub,
    "minute" / c.Int8ub,
    "second" / c.Int8ub,
    c.Bytes(4),
    "val" / c.Computed(lambda ctx: datetime.datetime(
        ctx.year, ctx.month, ctx.day,
        ctx.hour, ctx.minute, ctx.second
    )),
)

ItemsCount = c.Struct(
    "item_type" / c.Const(b'\x02'),
    "val" / c.Int8ub,
)

Text = c.Struct(
    "item_type" / c.Const(b'\x09'),
    "item_length" / c.Int8ub,
    "val" / c.PaddedString(c.this.item_length, 'utf8'),
)

ItemUint32 = c.Struct(
    "item_type" / c.Const(b'\x06'),
    "val" / c.Int32ub,
)

ItemInt32 = c.Struct(
    "item_type" / c.Const(b'\x06'),  # TODO: This looks odd, but Kaifa states that Current is signed.
    "val" / c.Int32sb,
)


# #############################
#  High level data collections
# #############################
List1 = c.Struct(
    "pwr_act_pos_item" / ItemUint32,

    "pwr_act_pos" / c.Computed(c.this.pwr_act_pos_item.val) * "W",
)

List2Top = c.Struct(
    "obis_version_item" / Text,
    "meter_id_item" / Text,
    "meter_type_item" / Text,
    "pwr_act_pos_item" / ItemUint32,
    "pwr_act_neg_item" / ItemUint32,
    "pwr_react_pos_item" / ItemUint32,
    "pwr_react_neg_item" / ItemUint32,

    "obis_version" / c.Computed(c.this.obis_version_item.val),
    "meter_id" / c.Computed(c.this.meter_id_item.val),
    "meter_type" / c.Computed(c.this.meter_type_item.val),
    "pwr_act_pos" / c.Computed(c.this.pwr_act_pos_item.val) * "W",
    "pwr_act_neg" / c.Computed(c.this.pwr_act_neg_item.val) * "W",
    "pwr_react_pos" / c.Computed(c.this.pwr_react_pos_item.val) * "VAr",
    "pwr_react_neg" / c.Computed(c.this.pwr_react_neg_item.val) * "VAr",
)

List2SinglePhase = c.Struct(
    c.Embedded(List2Top),
    "IL1_item" / ItemInt32,
    "ULN1_item" / ItemUint32,

    "IL1" / c.Computed(c.this.IL1_item.val / 1000) * "A",
    "ULN1" / c.Computed(c.this.ULN1_item.val / 10) * "V",
)

List2ThreePhase = c.Struct(
    c.Embedded(List2Top),
    "IL1_item" / ItemInt32,
    "IL2_item" / ItemInt32,
    "IL3_item" / ItemInt32,
    "ULN1_item" / ItemUint32,
    "ULN2_item" / ItemUint32,
    "ULN3_item" / ItemUint32,

    "IL1" / c.Computed(c.this.IL1_item.val / 1000) * "A",
    "IL2" / c.Computed(c.this.IL2_item.val / 1000) * "A",
    "IL3" / c.Computed(c.this.IL3_item.val / 1000) * "A",
    "ULN1" / c.Computed(c.this.ULN1_item.val / 10) * "V",
    "ULN2" / c.Computed(c.this.ULN2_item.val / 10) * "V",
    "ULN3" / c.Computed(c.this.ULN3_item.val / 10) * "V",
)

List3Items = c.Struct(
    "meter_ts_item" / Timestamp,
    "energy_act_pos_item" / ItemUint32,
    "energy_act_neg_item" / ItemUint32,
    "energy_react_pos_item" / ItemUint32,
    "energy_react_neg_item" / ItemUint32,

    "meter_ts" / c.Computed(c.this.meter_ts_item.val),
    "energy_act_pos" / c.Computed(c.this.energy_act_pos_item.val) * "Wh",
    "energy_act_neg" / c.Computed(c.this.energy_act_neg_item.val) * "Wh",
    "energy_react_pos" / c.Computed(c.this.energy_react_pos_item.val) * "VArh",
    "energy_react_neg" / c.Computed(c.this.energy_react_neg_item.val) * "VArh",
)

List3SinglePhase = c.Struct(
    c.Embedded(List2SinglePhase),
    c.Embedded(List3Items),
)

List3ThreePhase = c.Struct(
    c.Embedded(List2ThreePhase),
    c.Embedded(List3Items),
)

MeterData = c.Struct(
    "meter_ts_item" / Timestamp,
    "meter_ts" / c.Computed(c.this.meter_ts_item.val),
    "items_count_item" / ItemsCount,
    "items_count" / c.Computed(c.this.items_count_item.val),
    "data" / c.Switch(c.this.items_count, {
        1: List1,
        9: List2SinglePhase,
        13: List2ThreePhase,
        14: List3SinglePhase,
        18: List3ThreePhase,
    }),
)

LlcPdu = c.Struct(
    "lsap_dest" / c.Byte,
    "lsap_src" / c.Byte,
    "llc_quality" / c.Byte,
    c.Bytes(5),
    "meter_data" / MeterData
)

# #####################
#  Top level message
# #####################
Message = c.Struct(
    "header" / Header,
    "llc_pdu" / LlcPdu,
    "footer" / Footer,
)


def decode_frame(frame):
    msg = Message.parse(frame)
    return msg


