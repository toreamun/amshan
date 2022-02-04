"""Kaifa tests."""
# pylint: disable = no-self-use
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from pprint import pprint

import construct

from han import kaifa
from tests.assert_utils import (
    assert_apdu,
    assert_obis_element,
)


no_list_1 = bytes.fromhex(
    "e6e700" "0f" "40000000" "090c07e3020401173416ff800000" "0201" "06000016dc"
)

no_list_2 = bytes.fromhex(
    (
        "e6e700"
        "0f"
        "40000000"
        "090c 07e40119060d091eff800000"
        "020d"
        "0907 4b464d5f303031"
        "0910 36393730363331343032363134343736"
        "0908 4d413330344833450600002611"
        "06 00000000"
        "06 00000000"
        "06 000001b3"
        "06 00008415"
        "06 00006dc7"
        "06 00004702"
        "06 00000878"
        "06 00000000"
        "06 0000088c"
    ).replace(" ", "")
)

no_list_3 = bytes.fromhex(
    (
        "e6e700"
        "0f"
        "40000000"
        "090c 07e40119060e000aff800000"
        "0212"
        "0907 4b464d5f303031"
        "0910 36393730363331343032363134343736"
        "0908 4d41333034483345"
        "06 00001328"
        "06 00000000"
        "06 00000000"
        "06 00000179"
        "06 000038eb"
        "06 00003d1b"
        "06 00002535"
        "06 00000891"
        "06 00000000"
        "06 0000089d"
        "090c 07e40119060e000aff800000"
        "06 04be76e8"
        "06 00000000"
        "06 000d922d"
        "06 0030feb4"
    ).replace(" ", "")
)

se_list = bytes.fromhex(
    (
        "e6e700"
        "0f"
        "40000000"
        "00"
        "0224"
        "09060100000281ff 09074b464d5f303031"
        "09060000600100ff 091037333430373334303733343037333430"
        "09060000600107ff 09074d413330344834"
        "09060100010700ff 0600000b00"
        "09060100020700ff 0600000000"
        "09060100030700ff 0600000000"
        "09060100040700ff 0600000042"
        "090601001f0700ff 0600001a7d"
        "09060100330700ff 0600000316"
        "09060100470700ff 06000017ed"
        "09060100200700ff 0600000912"
        "09060100340700ff 06000008fc"
        "09060100480700ff 06000008f1"
        "09060000010000ff 090c07e509160311231effffc400"
        "09060100010800ff 0600490b23"
        "09060100020800ff 0600000000"
        "09060100030800ff 0600006674"
        "09060100040800ff 060008d3e0"
    ).replace(" ", "")
)


class TestParseKaifa:
    """Test parse Kaifa frames."""

    def test_parse_se_list(self):
        """Parse SE list."""
        parsed = kaifa.LlcPdu.parse(se_list)
        print(parsed)
        assert_apdu(parsed, 4194304, 0)
        assert (
            parsed.information.notification_body.type
            == kaifa.KaifaBodyType.OBIS_ELEMENTS
        )
        assert parsed.information.notification_body.length == 18
        assert_obis_element(
            parsed.information.notification_body.list_items[0],
            "1.0.0.2.129.255",
            "octet_string",
            "KFM_001",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[1],
            "0.0.96.1.0.255",
            "octet_string",
            "7340734073407340",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[2],
            "0.0.96.1.7.255",
            "octet_string",
            "MA304H4",
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[3],
            "1.0.1.7.0.255",
            "double_long_unsigned",
            2816,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[4],
            "1.0.2.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[5],
            "1.0.3.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[6],
            "1.0.4.7.0.255",
            "double_long_unsigned",
            66,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[7],
            "1.0.31.7.0.255",
            "double_long_unsigned",
            6781,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[8],
            "1.0.51.7.0.255",
            "double_long_unsigned",
            790,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[9],
            "1.0.71.7.0.255",
            "double_long_unsigned",
            6125,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[10],
            "1.0.32.7.0.255",
            "double_long_unsigned",
            2322,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[11],
            "1.0.52.7.0.255",
            "double_long_unsigned",
            2300,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[12],
            "1.0.72.7.0.255",
            "double_long_unsigned",
            2289,
        )
        date_time = parsed.information.notification_body.list_items[13]
        assert isinstance(date_time, construct.Container)
        assert date_time.obis == "0.0.1.0.0.255"
        assert date_time.value_type == "octet_string"
        assert date_time.value.datetime == datetime(
            2021, 9, 22, 17, 35, 30, tzinfo=timezone(timedelta(hours=1))
        )

        assert_obis_element(
            parsed.information.notification_body.list_items[14],
            "1.0.1.8.0.255",
            "double_long_unsigned",
            4786979,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[15],
            "1.0.2.8.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[16],
            "1.0.3.8.0.255",
            "double_long_unsigned",
            26228,
        )
        assert_obis_element(
            parsed.information.notification_body.list_items[17],
            "1.0.4.8.0.255",
            "double_long_unsigned",
            578528,
        )

    def test_parse_no_list_1(self):
        """Parse NO list number 1."""
        parsed = kaifa.LlcPdu.parse(no_list_1)
        print(parsed)
        assert_apdu(parsed, 4194304, datetime(2019, 2, 4, 23, 52, 22))

        assert (
            parsed.information.notification_body.type
            == kaifa.KaifaBodyType.VALUE_ELEMENTS
        )
        assert parsed.information.notification_body.length == 1
        assert parsed.information.notification_body.list_items[0].index == 0
        assert parsed.information.notification_body.list_items[0].value == 5852

    def test_parse_no_list_2(self):
        """Parse NO list number 2."""
        parsed = kaifa.LlcPdu.parse(no_list_2)
        print(parsed)
        assert_apdu(parsed, 4194304, datetime(2020, 1, 25, 13, 9, 30))
        assert parsed.information.notification_body.length == 13
        assert parsed.information.notification_body.list_items[0].index == 0
        assert parsed.information.notification_body.list_items[0].value == "KFM_001"
        assert parsed.information.notification_body.list_items[1].index == 1
        assert (
            parsed.information.notification_body.list_items[1].value
            == "6970631402614476"
        )
        assert parsed.information.notification_body.list_items[2].index == 2
        assert parsed.information.notification_body.list_items[2].value == "MA304H3E"
        assert parsed.information.notification_body.list_items[3].index == 3
        assert parsed.information.notification_body.list_items[3].value == 9745
        assert parsed.information.notification_body.list_items[4].index == 4
        assert parsed.information.notification_body.list_items[4].value == 0
        assert parsed.information.notification_body.list_items[5].index == 5
        assert parsed.information.notification_body.list_items[5].value == 0
        assert parsed.information.notification_body.list_items[6].index == 6
        assert parsed.information.notification_body.list_items[6].value == 435
        assert parsed.information.notification_body.list_items[7].index == 7
        assert parsed.information.notification_body.list_items[7].value == 33813
        assert parsed.information.notification_body.list_items[8].index == 8
        assert parsed.information.notification_body.list_items[8].value == 28103
        assert parsed.information.notification_body.list_items[9].index == 9
        assert parsed.information.notification_body.list_items[9].value == 18178
        assert parsed.information.notification_body.list_items[10].index == 10
        assert parsed.information.notification_body.list_items[10].value == 2168
        assert parsed.information.notification_body.list_items[11].index == 11
        assert parsed.information.notification_body.list_items[11].value == 0
        assert parsed.information.notification_body.list_items[12].index == 12
        assert parsed.information.notification_body.list_items[12].value == 2188

    def test_parse_no_list_3(self):
        """Parse NO list number 3."""
        parsed = kaifa.LlcPdu.parse(no_list_3)
        print(parsed)
        assert_apdu(parsed, 4194304, datetime(2020, 1, 25, 14, 0, 10))
        assert (
            parsed.information.notification_body.type
            == kaifa.KaifaBodyType.VALUE_ELEMENTS
        )
        assert parsed.information.notification_body.length == 18
        assert parsed.information.notification_body.list_items[0].index == 0
        assert parsed.information.notification_body.list_items[0].value == "KFM_001"
        assert parsed.information.notification_body.list_items[1].index == 1
        assert (
            parsed.information.notification_body.list_items[1].value
            == "6970631402614476"
        )
        assert parsed.information.notification_body.list_items[2].index == 2
        assert parsed.information.notification_body.list_items[2].value == "MA304H3E"
        assert parsed.information.notification_body.list_items[3].index == 3
        assert parsed.information.notification_body.list_items[3].value == 4904
        assert parsed.information.notification_body.list_items[4].index == 4
        assert parsed.information.notification_body.list_items[4].value == 0
        assert parsed.information.notification_body.list_items[5].index == 5
        assert parsed.information.notification_body.list_items[5].value == 0
        assert parsed.information.notification_body.list_items[6].index == 6
        assert parsed.information.notification_body.list_items[6].value == 377
        assert parsed.information.notification_body.list_items[7].index == 7
        assert parsed.information.notification_body.list_items[7].value == 14571
        assert parsed.information.notification_body.list_items[8].index == 8
        assert parsed.information.notification_body.list_items[8].value == 15643
        assert parsed.information.notification_body.list_items[9].index == 9
        assert parsed.information.notification_body.list_items[9].value == 9525
        assert parsed.information.notification_body.list_items[10].index == 10
        assert parsed.information.notification_body.list_items[10].value == 2193
        assert parsed.information.notification_body.list_items[11].index == 11
        assert parsed.information.notification_body.list_items[11].value == 0
        assert parsed.information.notification_body.list_items[12].index == 12
        assert parsed.information.notification_body.list_items[12].value == 2205
        assert parsed.information.notification_body.list_items[13].index == 13
        assert parsed.information.notification_body.list_items[
            13
        ].value.datetime == datetime(2020, 1, 25, 14, 0, 10)
        assert parsed.information.notification_body.list_items[14].index == 14
        assert parsed.information.notification_body.list_items[14].value == 79591144
        assert parsed.information.notification_body.list_items[15].index == 15
        assert parsed.information.notification_body.list_items[15].value == 0
        assert parsed.information.notification_body.list_items[16].index == 16
        assert parsed.information.notification_body.list_items[16].value == 889389
        assert parsed.information.notification_body.list_items[17].index == 17
        assert parsed.information.notification_body.list_items[17].value == 3210932


class TestDecodeKaifa:
    """Test decode Kaifa frames."""

    def test_decode_frame_se_list(self):
        """Decode SE list."""
        decoded = kaifa.decode_frame_content(se_list)
        pprint(decoded)
        assert isinstance(decoded, dict)
        assert len(decoded) == 19
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_export_total"] == 0
        assert decoded["active_power_import"] == 2816
        assert decoded["active_power_import_total"] == 4786979
        assert decoded["current_l1"] == 6.781
        assert decoded["current_l2"] == 0.79
        assert decoded["current_l3"] == 6.125
        assert decoded["list_ver_id"] == "KFM_001"
        assert decoded["meter_datetime"] == datetime(
            2021, 9, 22, 17, 35, 30, tzinfo=timezone(timedelta(hours=1))
        )
        assert decoded["meter_id"] == "7340734073407340"
        assert decoded["meter_manufacturer"] == "Kaifa"
        assert decoded["meter_type"] == "MA304H4"
        assert decoded["reactive_power_export"] == 66
        assert decoded["reactive_power_export_total"] == 578528
        assert decoded["reactive_power_import"] == 0
        assert decoded["reactive_power_import_total"] == 26228
        assert decoded["voltage_l1"] == 232.2
        assert decoded["voltage_l2"] == 230.0
        assert decoded["voltage_l3"] == 228.9

    def test_decode_frame_no_list_1(self):
        """Decode NO list number 1."""
        decoded = kaifa.decode_frame_content(no_list_1)
        pprint(decoded)
        assert isinstance(decoded, dict)
        assert len(decoded) == 3
        assert decoded["active_power_import"] == 5852
        assert decoded["meter_datetime"] == datetime(2019, 2, 4, 23, 52, 22)
        assert decoded["meter_manufacturer"] == "Kaifa"

    def test_decode_frame_no_list_2(self):
        """Decode NO list number 2."""
        decoded = kaifa.decode_frame_content(no_list_2)
        pprint(decoded)
        assert isinstance(decoded, dict)
        assert len(decoded) == 15
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_import"] == 9745
        assert decoded["current_l1"] == 33.813
        assert decoded["current_l2"] == 28.103
        assert decoded["current_l3"] == 18.178
        assert decoded["list_ver_id"] == "KFM_001"
        assert decoded["meter_datetime"] == datetime(2020, 1, 25, 13, 9, 30)
        assert decoded["meter_manufacturer"] == "Kaifa"
        assert decoded["meter_type"] == "MA304H3E"
        assert decoded["reactive_power_export"] == 435
        assert decoded["reactive_power_import"] == 0
        assert decoded["voltage_l1"] == 216.8
        assert decoded["voltage_l2"] == 0.0
        assert decoded["voltage_l3"] == 218.8

    def test_decode_frame_no_list_3(self):
        """Decode NO list number 3."""
        decoded = kaifa.decode_frame_content(no_list_3)
        pprint(decoded)
        assert isinstance(decoded, dict)
        assert len(decoded) == 19
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_export_total"] == 0
        assert decoded["active_power_import"] == 4904
        assert decoded["active_power_import_total"] == 79591144
        assert decoded["current_l1"] == 14.571
        assert decoded["current_l2"] == 15.643
        assert decoded["current_l3"] == 9.525
        assert decoded["list_ver_id"] == "KFM_001"
        assert decoded["meter_datetime"] == datetime(2020, 1, 25, 14, 0, 10)
        assert decoded["meter_id"] == "6970631402614476"
        assert decoded["meter_manufacturer"] == "Kaifa"
        assert decoded["meter_type"] == "MA304H3E"
        assert decoded["reactive_power_export"] == 377
        assert decoded["reactive_power_export_total"] == 3210932
        assert decoded["reactive_power_import"] == 0
        assert decoded["reactive_power_import_total"] == 889389
        assert decoded["voltage_l1"] == 219.3
        assert decoded["voltage_l2"] == 0.0
        assert decoded["voltage_l3"] == 220.5
