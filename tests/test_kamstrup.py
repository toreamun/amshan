"""Kamstrup tests."""
# pylint: disable = no-self-use
from __future__ import annotations
from datetime import datetime
from pprint import pprint

import construct

from han import kamstrup
from tests.assert_utils import (
    assert_apdu,
    assert_obis_element,
)

# Kamstrup example 1: 10 seconds list, three-phases, four-quadrants
no_list_1_three_phase = bytes.fromhex(
    (
        "E6 E7 00"  # LLC: dsap, ssap, control
        "0F"  # APDU: tag
        "00000000"  # APDU: LongInvokeIdAndPriority
        "0C07D0010106162100FF800001"  # APDU: DateTime
        "0219"  # structure of 0x19 elements
        "0A0E 4B616D73747275705F5630303031"  # visible_string
        "0906 0101000005FF  0A10 35373036353637303030303030303030"  # octet_string (obis) + visible_string
        "0906 0101600101FF  0A12 303030303030303030303030303030303030"  # octet_string (obis) + visible_string
        "0906 0101010700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101020700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101030700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101040700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 01011F0700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101330700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101470700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101200700FF  12 0000"  # octet_string (obis) + long_unsigned
        "0906 0101340700FF  12 0000"  # octet_string (obis) + long_unsigned
        "0906 0101480700FF  12 0000"  # octet_string (obis) + long_unsigned
    ).replace(" ", "")
)

# Kamstrup example 3: 1 hour list, single-phase, one-quadrant
no_list_2_single_phase = bytes.fromhex(
    (
        "E6 E7 00"  # LLC: dsap, ssap, control
        "0F"  # APDU: tag
        "00000000"  # APDU: LongInvokeIdAndPriority
        "0C07E1081003100005FF800000"  # APDU: DateTime
        "020F"  # structure of 0x0f elements
        "0A0E 4B616D73747275705F5630303031"  # visible_string
        "0906 0101000005FF  0A10 35373036353637303030303030303030"
        "0906 0101600101FF  0A12 303030303030303030303030303030303030"
        "0906 0101010700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 01011F0700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101200700FF  12 0000"  # octet_string (obis) + long_unsigned
        "0906 0001010000FF  090C 07E1081003100005FF800000"  # octet_string (obis) + octet_string
        "0906 0101010800FF  0600000000"  # octet_string + double_long_unsigned
    ).replace(" ", "")
)

# Kamstrup example 2: 1 hour list, three-phases, four-quadrants
no_list_2_three_phase = bytes.fromhex(
    (
        "E6 E 700"  # LLC: dsap, ssap, control
        "0F"  # APDU: tag
        "00000000"  # APDU: LongInvokeIdAndPriority
        "0C07E1081003100005FF800000"  # APDU: DateTime
        "0223"  # structure of 0x23 elements
        "0A0E 4B616D73747275705F5630303031"  # visible_string
        "0906 0101000005FF  0A10 35373036353637303030303030303030"
        "0906 0101600101FF  0A12 303030303030303030303030303030303030"
        "0906 0101010700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101020700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101030700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101040700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 01011F0700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101330700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101470700FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101200700FF  12 0000"  # octet_string (obis) + long_unsigned
        "0906 0101340700FF  12 0000"  # octet_string (obis) + long_unsigned
        "0906 0101480700FF  12 0000"  # octet_string (obis) + long_unsigned
        "0906 0001010000FF  090C 07E1081003100005FF800000"  # octet_string (obis) + octet_string
        "0906 0101010800FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101020800FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101030800FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101040800FF  06 00000000"  # octet_string (obis) + double_long_unsigned
    ).replace(" ", "")
)

no_list_1_single_phase_real_sample = bytes.fromhex(
    (
        "e6 e7 00"
        "0f"
        "000000000"
        "c07e60111010c2c28ff800000"
        "0219"
        "0a0e 4b616d73747275705f5630303031"  # OBIS List version identifier
        "0906 0101000005ff  0a10 35373035373035373035373035373032"  # 1.1.0.0.5.255 (GS1 number)
        "0906 0101600101ff  0a12 36383631313131424e323432313031303430"  # 1.1.96.1.1.255 (Meter type)
        "0906 0101010700ff  0600000768"  # 1.1.1.7.0.255 (P14)
        "0906 0101020700ff  0600000000"  # 1.1.2.7.0.255 (P23)
        "0906 0101030700ff  0600000000"  # 1.1.3.7.0.255 (Q12)
        "0906 0101040700ff  06000001ed"  # 1.1.4.7.0.255 (Q34)
        "0906 01011f0700ff  0600000380"  # 1.1.31.7.0.255 (IL1)
        "00000000"
        "0906 0101200700ff  1200e1"  # 1.1.32.7.0.255 (UL1)
        "00000000"
    ).replace(" ", "")
)

no_list_2_single_phase_real_sample = bytes.fromhex(
    (
        "e6e700"
        "0f"
        "000000000"
        "c07e50b1803000019ff800000"
        "0223"
        "0a0e 4b616d73747275705f5630303031"
        "0906 0101000005ff  0a10 35373035373035373035373035373032"
        "0906 0101600101ff  0a12 36383631313131424e323432313031303430"
        "0906 0101010700ff  06 00002742"
        "0906 0101020700ff  06 00000000"
        "0906 0101030700ff  06 00000000"
        "0906 0101040700ff  06 00000117"
        "0906 01011f0700ff  06 000011a000000000"
        "0906 0101200700ff  12 00df00000000"
        "0906 0001010000ff  090c 07e50b1803000019ff800000"
        "0906 0101010800ff  06 00762ee2"
        "0906 0101020800ff  06 00000000"
        "0906 0101030800ff  06 000035a3"
        "0906 0101040800ff  06 00116b53"
    ).replace(" ", "")
)

# 7E A0 E2 2B 21 13 23 9A E6 E7 00 0F 00 00 00 00 0C 07 E6 01 18 01 12 3A 32 FF 80 00 00 02 19 0A 0E 4B 61 6D 73 74 72 75 70 5F 56 30 30 30 31 09 06 01 01 00 00 05 FF 0A 10 35 37 30 36 35 36 37 33 32 36 35 39 30 34 30 37 09 06 01 01 60 01 01 FF 0A 12 36 38 34 31 31 33 38 42 4E 32 34 35 31 30 31 30 39 30 09 06 01 01 01 07 00 FF 06 00 00 03 3A 09 06 01 01 02 07 00 FF 06 00 00 00 00 09 06 01 01 03 07 00 FF 06 00 00 00 68 09 06 01 01 04 07 00 FF 06 00 00 00 B0 09 06 01 01 1F 07 00 FF 06 00 00 00 ED 09 06 01 01 33 07 00 FF 06 00 00 00 59 09 06 01 01 47 07 00 FF 06 00 00 00 4B 09 06 01 01 20 07 00 FF 12 00 E8 09 06 01 01 34 07 00 FF 12 00 E9 09 06 01 01 48 07 00 FF 12 00 EC 84 46 7E

# 7EA0E22B2113239AE6E7000F000000000C07E6011801123A32FF80000002190A0E4B616D73747275705F563030303109060101000005FF0A103537303635363733323635393034303709060101600101FF0A1236383431313338424E32343531303130393009060101010700FF060000033A09060101020700FF060000000009060101030700FF060000006809060101040700FF06000000B0090601011F0700FF06000000ED09060101330700FF060000005909060101470700FF060000004B09060101200700FF1200E809060101340700FF1200E909060101480700FF1200EC84467E

se_list_real_sample = bytes.fromhex(
    (
        "E6E700"
        "0F"
        "000000000"
        "C07E6011801123A32FF800000"
        "0219"
        "0A0E 4B616D73747275705F5630303031"
        "0906 0101000005FF"
        "0A10 35373035373035373035373035373037  0906 0101600101FF"
        "0A12 36383431313338424E323435313031303930  09060101010700FF060000033A"
        "0906 0101020700FF  0600000000"
        "0906 0101030700FF  0600000068"
        "0906 0101040700FF  06000000B0"
        "0906 01011F0700FF  06000000ED"
        "0906 0101330700FF  0600000059"
        "0906 0101470700FF  060000004B"
        "0906 0101200700FF  1200E8"
        "0906 0101340700FF  1200E9"
        "0906 0101480700FF  1200EC"
    ).replace(" ", "")
)


class TestParseKamstrup:
    """Test parse Kamstrup frames."""

    def test_parse_se_list_three_phase_real_sample(self):
        """Parse SE list."""
        parsed = kamstrup.LlcPdu.parse(se_list_real_sample)

        print(parsed)

        assert_apdu(parsed, 0, datetime(2022, 1, 24, 18, 58, 50))
        assert isinstance(parsed.information.notification_body, construct.Container)
        assert parsed.information.notification_body.length == 0x19
        assert isinstance(
            parsed.information.notification_body.list_items, construct.ListContainer
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[0],
            None,
            "visible_string",
            "Kamstrup_V0001",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[1],
            "1.1.0.0.5.255",  # GS1 number
            "visible_string",
            "5705705705705707",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[2],
            "1.1.96.1.1.255",  # Meter type
            "visible_string",
            "6841138BN245101090",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[3],
            "1.1.1.7.0.255",  # P14
            "double_long_unsigned",
            826,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[4],
            "1.1.2.7.0.255",  # P23
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[5],
            "1.1.3.7.0.255",  # Q12
            "double_long_unsigned",
            104,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[6],
            "1.1.4.7.0.255",  # Q34
            "double_long_unsigned",
            176,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[7],
            "1.1.31.7.0.255",  # IL1
            "double_long_unsigned",
            237,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[8],
            "1.1.51.7.0.255",  # IL2
            "double_long_unsigned",
            89,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[9],
            "1.1.71.7.0.255",  # IL3
            "double_long_unsigned",
            75,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[10],
            "1.1.32.7.0.255",  # UL1
            "long_unsigned",
            232,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[11],
            "1.1.52.7.0.255",  # UL2
            "long_unsigned",
            233,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[12],
            "1.1.72.7.0.255",  # UL3
            "long_unsigned",
            236,
        )

    def test_parse_no_list_1_single_phase_real_sample(self):
        """Parse single phase NO list number 1."""
        parsed = kamstrup.LlcPdu.parse(no_list_1_single_phase_real_sample)

        print(parsed)

        assert_apdu(parsed, 0, datetime(2022, 1, 17, 12, 44, 40))
        assert isinstance(parsed.information.notification_body, construct.Container)
        assert parsed.information.notification_body.length == 0x19
        assert isinstance(
            parsed.information.notification_body.list_items, construct.ListContainer
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[0],
            None,
            "visible_string",
            "Kamstrup_V0001",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[1],
            "1.1.0.0.5.255",  # GS1 number
            "visible_string",
            "5705705705705702",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[2],
            "1.1.96.1.1.255",  # Meter type
            "visible_string",
            "6861111BN242101040",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[3],
            "1.1.1.7.0.255",  # P14
            "double_long_unsigned",
            1896,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[4],
            "1.1.2.7.0.255",  # P23
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[5],
            "1.1.3.7.0.255",  # Q12
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[6],
            "1.1.4.7.0.255",  # Q34
            "double_long_unsigned",
            493,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[7],
            "1.1.31.7.0.255",  # IL1
            "double_long_unsigned",
            896,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[8],
            "1.1.32.7.0.255",  # UL1
            "long_unsigned",
            225,
        )

    def test_parse_no_list_2_single_phase_real_sample(self):
        """Parse single phase NO list number 1."""
        parsed = kamstrup.LlcPdu.parse(no_list_2_single_phase_real_sample)

        print(parsed)

        assert_apdu(parsed, 0, datetime(2021, 11, 24, 0, 0, 25))
        assert isinstance(parsed.information.notification_body, construct.Container)
        assert parsed.information.notification_body.length == 35
        assert isinstance(
            parsed.information.notification_body.list_items, construct.ListContainer
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[0],
            None,
            "visible_string",
            "Kamstrup_V0001",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[1],
            "1.1.0.0.5.255",  # GS1 number
            "visible_string",
            "5705705705705702",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[2],
            "1.1.96.1.1.255",  # Meter type
            "visible_string",
            "6861111BN242101040",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[3],
            "1.1.1.7.0.255",  # P14
            "double_long_unsigned",
            10050,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[4],
            "1.1.2.7.0.255",  # P23
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[5],
            "1.1.3.7.0.255",  # Q12
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[6],
            "1.1.4.7.0.255",  # Q34
            "double_long_unsigned",
            279,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[7],
            "1.1.31.7.0.255",  # IL1
            "double_long_unsigned",
            4512,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[8],
            "1.1.32.7.0.255",  # UL1
            "long_unsigned",
            223,
        )

        rtc = parsed.information.notification_body.list_items[9]
        assert isinstance(rtc, construct.Container)
        assert rtc.obis == "0.1.1.0.0.255"  # RTC
        assert rtc.value_type == "octet_string"
        assert rtc.value.datetime == datetime(2021, 11, 24, 0, 0, 25)

        assert_obis_element(
            parsed.information.notification_body.list_items[10],
            "1.1.1.8.0.255",  # A14
            "double_long_unsigned",
            7745250,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[11],
            "1.1.2.8.0.255",  # A23
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[12],
            "1.1.3.8.0.255",  # R12
            "double_long_unsigned",
            13731,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[13],
            "1.1.4.8.0.255",  # R12
            "double_long_unsigned",
            1141587,
        )

    def test_parse_no_list_1_three_phase(self):
        """Parse three phase NO list number 1."""
        parsed = kamstrup.LlcPdu.parse(no_list_1_three_phase)
        print(parsed)

        assert_apdu(parsed, 0, datetime(2000, 1, 1, 22, 33, 0))
        assert parsed.information.notification_body.length == 0x19
        assert isinstance(
            parsed.information.notification_body.list_items, construct.ListContainer
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[0],
            None,
            "visible_string",
            "Kamstrup_V0001",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[1],
            "1.1.0.0.5.255",  # GS1 number
            "visible_string",
            "5706567000000000",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[2],
            "1.1.96.1.1.255",  # Meter type
            "visible_string",
            "000000000000000000",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[3],
            "1.1.1.7.0.255",  # P14
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[4],
            "1.1.2.7.0.255",  # P23
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[5],
            "1.1.3.7.0.255",  # Q12
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[6],
            "1.1.4.7.0.255",  # Q34
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[7],
            "1.1.31.7.0.255",  # IL1
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[8],
            "1.1.51.7.0.255",  # IL2
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[9],
            "1.1.71.7.0.255",  # IL3
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[10],
            "1.1.32.7.0.255",  # UL1
            "long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[11],
            "1.1.52.7.0.255",  # UL2
            "long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[12],
            "1.1.72.7.0.255",  # UL3
            "long_unsigned",
            0,
        )

    def test_parse_no_list_2_single_phase(self):
        """Parse single phase NO list number 2."""
        parsed = kamstrup.LlcPdu.parse(no_list_2_single_phase)

        print(parsed)

        assert_apdu(parsed, 0, datetime(2017, 8, 16, 16, 0, 5))
        assert parsed.information.notification_body.length == 15
        assert isinstance(
            parsed.information.notification_body.list_items, construct.ListContainer
        )

    def test_parse_no_list_2_three_phase(self):
        """Parse three phase NO list number 2."""
        parsed = kamstrup.LlcPdu.parse(no_list_2_three_phase)

        print(parsed)

        assert_apdu(parsed, 0, datetime(2017, 8, 16, 16, 0, 5))
        assert parsed.information.notification_body.length == 35
        assert isinstance(
            parsed.information.notification_body.list_items, construct.ListContainer
        )


class TestDecodeKamstrup:
    """Test decode Kamstrup frames."""

    def test_decode_se_list_three_phase_real_sample(self):
        """Decode three phase SE list (real sample)."""
        decoded = kamstrup.decode_frame_content(se_list_real_sample)
        pprint(decoded)
        assert isinstance(decoded, dict)
        assert len(decoded) == 15
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_import"] == 826
        assert decoded["current_l1"] == 2.37
        assert decoded["current_l2"] == 0.89
        assert decoded["current_l3"] == 0.75
        assert decoded["list_ver_id"] == "Kamstrup_V0001"
        assert decoded["meter_datetime"] == datetime(2022, 1, 24, 18, 58, 50)
        assert decoded["meter_id"] == "5705705705705707"
        assert decoded["meter_manufacturer"] == "Kamstrup"
        assert decoded["meter_type"] == "6841138BN245101090"
        assert decoded["reactive_power_export"] == 176
        assert decoded["reactive_power_import"] == 104
        assert decoded["voltage_l1"] == 232
        assert decoded["voltage_l2"] == 233
        assert decoded["voltage_l3"] == 236

    def test_decode_frame_no_list_1_single_phase_real_sample(self):
        """Decode three phase no list number 1."""
        decoded = kamstrup.decode_frame_content(no_list_1_single_phase_real_sample)
        pprint(decoded)
        assert isinstance(decoded, dict)
        assert len(decoded) == 11
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_import"] == 1896
        assert decoded["current_l1"] == 8.96
        assert decoded["list_ver_id"] == "Kamstrup_V0001"
        assert decoded["meter_datetime"] == datetime(2022, 1, 17, 12, 44, 40)
        assert decoded["meter_id"] == "5705705705705702"
        assert decoded["meter_manufacturer"] == "Kamstrup"
        assert decoded["meter_type"] == "6861111BN242101040"
        assert decoded["reactive_power_export"] == 493
        assert decoded["reactive_power_import"] == 0
        assert decoded["voltage_l1"] == 225

    def test_decode_frame_no_list_2_single_phase_real_sample(self):
        """Decode three phase no list number 1."""
        decoded = kamstrup.decode_frame_content(no_list_2_single_phase_real_sample)
        pprint(decoded)
        assert isinstance(decoded, dict)
        assert len(decoded) == 15
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_export_total"] == 0
        assert decoded["active_power_import"] == 10050
        assert decoded["active_power_import_total"] == 77452500
        assert decoded["current_l1"] == 45.12
        assert decoded["list_ver_id"] == "Kamstrup_V0001"
        assert decoded["meter_datetime"] == datetime(2021, 11, 24, 0, 0, 25)
        assert decoded["meter_id"] == "5705705705705702"
        assert decoded["meter_manufacturer"] == "Kamstrup"
        assert decoded["meter_type"] == "6861111BN242101040"
        assert decoded["reactive_power_export"] == 279
        assert decoded["reactive_power_export_total"] == 11415870
        assert decoded["reactive_power_import"] == 0
        assert decoded["reactive_power_import_total"] == 137310
        assert decoded["voltage_l1"] == 223

    def test_decode_frame_no_list_1_three_phase(self):
        """Decode three phase no list number 1."""
        decoded = kamstrup.decode_frame_content(no_list_1_three_phase)
        pprint(decoded)
        assert isinstance(decoded, dict)
        assert len(decoded) == 15
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_import"] == 0
        assert decoded["current_l1"] == 0.0
        assert decoded["current_l2"] == 0.0
        assert decoded["current_l3"] == 0.0
        assert decoded["list_ver_id"] == "Kamstrup_V0001"
        assert decoded["meter_datetime"] == datetime(2000, 1, 1, 22, 33)
        assert decoded["meter_id"] == "5706567000000000"
        assert decoded["meter_manufacturer"] == "Kamstrup"
        assert decoded["meter_type"] == "000000000000000000"
        assert decoded["reactive_power_export"] == 0
        assert decoded["reactive_power_import"] == 0
        assert decoded["voltage_l1"] == 0
        assert decoded["voltage_l2"] == 0
        assert decoded["voltage_l3"] == 0

    def test_decode_frame_no_list_2_three_phase(self):
        """Decode three phase no list number 2."""
        decoded = kamstrup.decode_frame_content(no_list_2_three_phase)
        pprint(decoded)
        assert isinstance(decoded, dict)
        assert len(decoded) == 19
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_export_total"] == 0
        assert decoded["active_power_import"] == 0
        assert decoded["active_power_import_total"] == 0
        assert decoded["current_l1"] == 0
        assert decoded["current_l2"] == 0
        assert decoded["current_l3"] == 0
        assert decoded["list_ver_id"] == "Kamstrup_V0001"
        assert decoded["meter_datetime"] == datetime(2017, 8, 16, 16, 0, 5)
        assert decoded["meter_id"] == "5706567000000000"
        assert decoded["meter_manufacturer"] == "Kamstrup"
        assert decoded["meter_type"] == "000000000000000000"
        assert decoded["reactive_power_export"] == 0
        assert decoded["reactive_power_export_total"] == 0
        assert decoded["reactive_power_import"] == 0
        assert decoded["reactive_power_import_total"] == 0
        assert decoded["voltage_l1"] == 0
        assert decoded["voltage_l2"] == 0
        assert decoded["voltage_l3"] == 0

    def test_decode_frame_no_list_2_single_phase(self):
        """Decode single phase no list number 2."""
        decoded = kamstrup.decode_frame_content(no_list_2_single_phase)
        pprint(decoded)
        assert isinstance(decoded, dict)
        assert len(decoded) == 9
        assert decoded["active_power_import"] == 0
        assert decoded["active_power_import_total"] == 0
        assert decoded["current_l1"] == 0.0
        assert decoded["list_ver_id"] == "Kamstrup_V0001"
        assert decoded["meter_datetime"] == datetime(2017, 8, 16, 16, 0, 5)
        assert decoded["meter_id"] == "5706567000000000"
        assert decoded["meter_manufacturer"] == "Kamstrup"
        assert decoded["meter_type"] == "000000000000000000"
        assert decoded["voltage_l1"] == 0
