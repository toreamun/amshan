"""Aidon tests."""
# pylint: disable = no-self-use
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pprint import pprint

import construct
import pytest

from han import aidon
from tests.assert_utils import assert_apdu

NOTIFICATION_BODY_NO_LIST_1 = "0101" + "020309060100010700ff060000011802020f00161b"

no_list_1 = bytes.fromhex(
    (
        "e6e700"  # LLC: dsap, ssap, control
        "0f"  # APDU: tag
        "40000000"  # APDU: LongInvokeIdAndPriority
        "00"  # APDU: DateTime
    )
    + NOTIFICATION_BODY_NO_LIST_1
)

NOTIFICATION_BODY_NO_LIST_2 = (
    "010c"
    "020209060101000281ff0a0b4149444f4e5f5630303031"
    "020209060000600100ff0a1037333539393932383932353837363635"
    "020209060000600107ff0a0436353235"
    "020309060100010700ff060000011802020f00161b"
    "020309060100020700ff060000000002020f00161b"
    "020309060100030700ff060000000002020f00161d"
    "020309060100040700ff060000008002020f00161d"
    "0203090601001f0700ff10000d02020fff1621"
    "020309060100470700ff10000902020fff1621"
    "020309060100200700ff1208e202020fff1623"
    "020309060100340700ff1208fd02020fff1623"
    "020309060100480700ff12090402020fff1623"
)

no_list_2 = bytes.fromhex(
    (
        "e6e700"  # LLC: dsap, ssap, control
        "0f"  # APDU: tag
        "40000000"  # APDU: LongInvokeIdAndPriority
        "00"  # APDU: DateTime
    )
    + NOTIFICATION_BODY_NO_LIST_2
)

NOTIFICATION_BODY_NO_LIST_3 = (
    "0111"
    "020209060101000281ff0a0b4149444f4e5f5630303031"
    "020209060000600100ff0a1037333539393932383932353837363635"
    "020209060000600107ff0a0436353235020309060100010700ff0600000118"
    "02020f00161b020309060100020700ff0600000000"
    "02020f00161b020309060100030700ff0600000000"
    "02020f00161d020309060100040700ff0600000080"
    "02020f00161d0203090601001f0700ff10000d"
    "02020fff1621020309060100470700ff100009"
    "02020fff1621020309060100200700ff1208e4"
    "02020fff1623020309060100340700ff1208ff"
    "02020fff1623020309060100480700ff120905"
    "02020fff1623020209060000010000ff090c07e4011502100000ff000000"
    "020309060100010800ff060022ab8a"
    "02020f01161e020309060100020800ff0600000000"
    "02020f01161e020309060100030800ff060000e383"
    "02020f011620020309060100040800ff0600029b5b"
    "02020f011620"
)

no_list_3 = bytes.fromhex(
    (
        "e6e700"  # LLC: dsap, ssap, control
        "0f"  # APDU: tag
        "40000000"  # APDU: LongInvokeIdAndPriority
        "00"  # APDU: DateTime
    )
    + NOTIFICATION_BODY_NO_LIST_3
)

# From https://www.tekniskaverken.se/siteassets/tekniska-verken/elnat/aidonfd-rj12-han-interface-sv-v15d.pdf
NOTIFICATION_BODY_SE_LIST = (
    "011b"
    "0202 0906 0000010000ff 090c 07e30c1001073b28ff8000ff"
    "0203 0906 0100010700ff 06 00000462 0202 0f00 161b"
    "0203 0906 0100020700ff 06 00000000 0202 0f00 161b"
    "0203 0906 0100030700ff 06 000005e3 0202 0f00 161d"
    "0203 0906 0100040700ff 06 00000000 0202 0f00 161d"
    "0203 0906 01001f0700ff 10 00000202 0fff 1621"
    "0203 0906 0100330700ff 10 004b0202 0fff 1621"
    "0203 0906 0100470700ff 10 00000202 0fff 1621"
    "0203 0906 0100200700ff 12 09030202 0fff 1623"
    "0203 0906 0100340700ff 12 09c30202 0fff 1623"
    "0203 0906 0100480700ff 12 09040202 0fff 1623"
    "0203 0906 0100150700ff 06 00000000 0202 0f00 161b"
    "0203 0906 0100160700ff 06 00000000 0202 0f00 161b"
    "0203 0906 0100170700ff 06 00000000 0202 0f00 161d"
    "0203 0906 0100180700ff 06 00000000 0202 0f00 161d"
    "0203 0906 0100290700ff 06 00000462 0202 0f00 161b"
    "0203 0906 01002a0700ff 06 00000000 0202 0f00 161b"
    "0203 0906 01002b0700ff 06 000005e2 0202 0f00 161d"
    "0203 0906 01002c0700ff 06 00000000 0202 0f00 161d"
    "0203 0906 01003d0700ff 06 00000000 0202 0f00 161b"
    "0203 0906 01003e0700ff 06 00000000 0202 0f00 161b"
    "0203 0906 01003f0700ff 06 00000000 0202 0f00 161d"
    "0203 0906 0100400700ff 06 00000000 0202 0f00 161d"
    "0203 0906 0100010800ff 06 00995986 0202 0f00 161e"
    "0203 0906 0100020800ff 06 00000008 0202 0f00 161e"
    "0203 0906 0100030800ff 06 0064ed4b 0202 0f00 1620"
    "0203 0906 0100040800ff 06 00000005 0202 0f00 1620"
).replace(" ", "")

se_list = bytes.fromhex(
    (
        (
            "e6e700"  # LLC: dsap, ssap, control
            "0f"  # APDU: tag
            "40000000"  # APDU: LongInvokeIdAndPriority
            "00"  # APDU: DateTime
        )
        + NOTIFICATION_BODY_SE_LIST
    ).replace(" ", "")
)


def assert_obis_element(
    container, expected_obis_code, expected_value_type, expected_value
):
    """Assert OBIS element is as expected."""
    assert isinstance(container, construct.Container)
    assert container.obis == expected_obis_code
    assert container.content_type == expected_value_type
    if isinstance(container.content, construct.Container):
        assert container.content.value == expected_value
    else:
        assert container.content == expected_value


class TestParseAidon:
    """Test parse Aidon frames."""

    @pytest.mark.parametrize(
        "llc_pdu,notification_body",
        [
            [se_list, None],
            [None, bytes.fromhex(NOTIFICATION_BODY_SE_LIST)],
        ],
    )
    def test_parse_se_list(self, llc_pdu, notification_body):
        """Parse swedish list number 1."""
        if llc_pdu is not None:
            parsed = aidon.LlcPdu.parse(llc_pdu)
            print(parsed)
            assert_apdu(parsed, 4194304, 0)
            parsed_notification_body = parsed.information.notification_body

        if notification_body is not None:
            parsed = aidon.NotificationBody.parse(notification_body)
            print(parsed)
            parsed_notification_body = parsed

        assert parsed_notification_body.length == 27
        assert isinstance(parsed_notification_body.list_items, construct.ListContainer)

        date_time = parsed_notification_body.list_items[0]
        assert date_time.obis == "0.0.1.0.0.255"
        assert date_time.content_type == "octet_string"
        assert date_time.content.datetime == datetime(2019, 12, 16, 7, 59, 40)

        assert_obis_element(
            parsed_notification_body.list_items[1],
            "1.0.1.7.0.255",
            "double_long_unsigned",
            1122,
        )
        assert_obis_element(
            parsed_notification_body.list_items[2],
            "1.0.2.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[3],
            "1.0.3.7.0.255",
            "double_long_unsigned",
            1507,
        )
        assert_obis_element(
            parsed_notification_body.list_items[4],
            "1.0.4.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[5],
            "1.0.31.7.0.255",
            "long",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[6],
            "1.0.51.7.0.255",
            "long",
            7.5,
        )
        assert_obis_element(
            parsed_notification_body.list_items[7],
            "1.0.71.7.0.255",
            "long",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[8],
            "1.0.32.7.0.255",
            "long_unsigned",
            Decimal("230.7"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[9],
            "1.0.52.7.0.255",
            "long_unsigned",
            Decimal("249.9"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[10],
            "1.0.72.7.0.255",
            "long_unsigned",
            Decimal("230.8"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[11],
            "1.0.21.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[12],
            "1.0.22.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[13],
            "1.0.23.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[14],
            "1.0.24.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[15],
            "1.0.41.7.0.255",
            "double_long_unsigned",
            1122,
        )
        assert_obis_element(
            parsed_notification_body.list_items[16],
            "1.0.42.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[17],
            "1.0.43.7.0.255",
            "double_long_unsigned",
            1506,
        )
        assert_obis_element(
            parsed_notification_body.list_items[18],
            "1.0.44.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[19],
            "1.0.61.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[20],
            "1.0.62.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[21],
            "1.0.63.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[22],
            "1.0.64.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[23],
            "1.0.1.8.0.255",
            "double_long_unsigned",
            10049926,
        )
        assert_obis_element(
            parsed_notification_body.list_items[24],
            "1.0.2.8.0.255",
            "double_long_unsigned",
            8,
        )
        assert_obis_element(
            parsed_notification_body.list_items[25],
            "1.0.3.8.0.255",
            "double_long_unsigned",
            6614347,
        )
        assert_obis_element(
            parsed_notification_body.list_items[26],
            "1.0.4.8.0.255",
            "double_long_unsigned",
            5,
        )

    @pytest.mark.parametrize(
        "llc_pdu,notification_body",
        [
            [no_list_1, None],
            [None, bytes.fromhex(NOTIFICATION_BODY_NO_LIST_1)],
        ],
    )
    def test_parse_no_list_1(self, llc_pdu, notification_body):
        """Parse list number 1."""
        if llc_pdu is not None:
            parsed = aidon.LlcPdu.parse(llc_pdu)
            print(parsed)
            assert_apdu(parsed, 4194304, 0)
            parsed_notification_body = parsed.information.notification_body

        if notification_body is not None:
            parsed = aidon.NotificationBody.parse(notification_body)
            print(parsed)
            parsed_notification_body = parsed

        assert parsed_notification_body.length == 1
        assert isinstance(parsed_notification_body.list_items, construct.ListContainer)
        assert_obis_element(
            parsed_notification_body.list_items[0],
            "1.0.1.7.0.255",
            "double_long_unsigned",
            280,
        )

    @pytest.mark.parametrize(
        "llc_pdu,notification_body",
        [
            [no_list_2, None],
            [None, bytes.fromhex(NOTIFICATION_BODY_NO_LIST_2)],
        ],
    )
    def test_parse_no_list_2(self, llc_pdu, notification_body):
        """Parse list number 2."""
        if llc_pdu is not None:
            parsed = aidon.LlcPdu.parse(llc_pdu)
            print(parsed)
            assert_apdu(parsed, 4194304, 0)
            parsed_notification_body = parsed.information.notification_body

        if notification_body is not None:
            parsed = aidon.NotificationBody.parse(notification_body)
            print(parsed)
            parsed_notification_body = parsed

        assert parsed_notification_body.length == 12
        assert isinstance(parsed_notification_body.list_items, construct.ListContainer)
        assert_obis_element(
            parsed_notification_body.list_items[0],
            "1.1.0.2.129.255",
            "visible_string",
            "AIDON_V0001",
        )
        assert_obis_element(
            parsed_notification_body.list_items[1],
            "0.0.96.1.0.255",
            "visible_string",
            "7359992892587665",
        )
        assert_obis_element(
            parsed_notification_body.list_items[2],
            "0.0.96.1.7.255",
            "visible_string",
            "6525",
        )
        assert_obis_element(
            parsed_notification_body.list_items[3],
            "1.0.1.7.0.255",
            "double_long_unsigned",
            280,
        )
        assert_obis_element(
            parsed_notification_body.list_items[4],
            "1.0.2.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[5],
            "1.0.3.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[6],
            "1.0.4.7.0.255",
            "double_long_unsigned",
            128,
        )
        assert_obis_element(
            parsed_notification_body.list_items[7],
            "1.0.31.7.0.255",
            "long",
            Decimal("1.3"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[8],
            "1.0.71.7.0.255",
            "long",
            Decimal("0.9"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[9],
            "1.0.32.7.0.255",
            "long_unsigned",
            Decimal("227.4"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[10],
            "1.0.52.7.0.255",
            "long_unsigned",
            Decimal("230.1"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[11],
            "1.0.72.7.0.255",
            "long_unsigned",
            Decimal("230.8"),
        )

    @pytest.mark.parametrize(
        "llc_pdu,notification_body",
        [
            [no_list_3, None],
            [None, bytes.fromhex(NOTIFICATION_BODY_NO_LIST_3)],
        ],
    )
    def test_parse_no_list_3(self, llc_pdu, notification_body):
        """Parse list number 2."""
        if llc_pdu is not None:
            parsed = aidon.LlcPdu.parse(llc_pdu)
            print(parsed)
            assert_apdu(parsed, 4194304, 0)
            parsed_notification_body = parsed.information.notification_body

        if notification_body is not None:
            parsed = aidon.NotificationBody.parse(notification_body)
            print(parsed)
            parsed_notification_body = parsed

        assert parsed_notification_body.length == 17
        assert isinstance(parsed_notification_body.list_items, construct.ListContainer)
        assert_obis_element(
            parsed_notification_body.list_items[0],
            "1.1.0.2.129.255",
            "visible_string",
            "AIDON_V0001",
        )
        assert_obis_element(
            parsed_notification_body.list_items[1],
            "0.0.96.1.0.255",
            "visible_string",
            "7359992892587665",
        )
        assert_obis_element(
            parsed_notification_body.list_items[2],
            "0.0.96.1.7.255",
            "visible_string",
            "6525",
        )
        assert_obis_element(
            parsed_notification_body.list_items[3],
            "1.0.1.7.0.255",
            "double_long_unsigned",
            280,
        )
        assert_obis_element(
            parsed_notification_body.list_items[4],
            "1.0.2.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[5],
            "1.0.3.7.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[6],
            "1.0.4.7.0.255",
            "double_long_unsigned",
            128,
        )
        assert_obis_element(
            parsed_notification_body.list_items[7],
            "1.0.31.7.0.255",
            "long",
            Decimal("1.3"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[8],
            "1.0.71.7.0.255",
            "long",
            Decimal("0.9"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[9],
            "1.0.32.7.0.255",
            "long_unsigned",
            Decimal("227.6"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[10],
            "1.0.52.7.0.255",
            "long_unsigned",
            Decimal("230.3"),
        )
        assert_obis_element(
            parsed_notification_body.list_items[11],
            "1.0.72.7.0.255",
            "long_unsigned",
            Decimal("230.9"),
        )
        date_time = parsed_notification_body.list_items[12]
        assert isinstance(date_time, construct.Container)
        assert date_time.obis == "0.0.1.0.0.255"
        assert date_time.content_type == "octet_string"
        assert date_time.content.datetime == datetime(
            2020, 1, 21, 16, 0, 0, tzinfo=timezone.utc
        )
        assert_obis_element(
            parsed_notification_body.list_items[13],
            "1.0.1.8.0.255",
            "double_long_unsigned",
            22721380,
        )
        assert_obis_element(
            parsed_notification_body.list_items[14],
            "1.0.2.8.0.255",
            "double_long_unsigned",
            0,
        )
        assert_obis_element(
            parsed_notification_body.list_items[15],
            "1.0.3.8.0.255",
            "double_long_unsigned",
            582430,
        )
        assert_obis_element(
            parsed_notification_body.list_items[16],
            "1.0.4.8.0.255",
            "double_long_unsigned",
            1708430,
        )


class TestDecodeAidon:
    """Test decode Aidon frames."""

    @pytest.mark.parametrize(
        "llc_pdu,notification_body",
        [
            [se_list, None],
            [None, bytes.fromhex(NOTIFICATION_BODY_SE_LIST)],
        ],
    )
    def test_decode_frame_se_list(self, llc_pdu, notification_body):
        """Decode SE list."""
        if llc_pdu is not None:
            decoded = aidon.decode_frame_content(llc_pdu)

        if notification_body is not None:
            decoded = aidon.decode_notification_body(notification_body)

        pprint(decoded)

        assert len(decoded) == 28
        assert isinstance(decoded, dict)
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_export_total"] == 8
        assert decoded["active_power_export_l1"] == 0
        assert decoded["active_power_export_l2"] == 0
        assert decoded["active_power_export_l3"] == 0
        assert decoded["active_power_import"] == 1122
        assert decoded["active_power_import_total"] == 10049926
        assert decoded["active_power_import_l1"] == 0
        assert decoded["active_power_import_l2"] == 1122
        assert decoded["current_l1"] == 0
        assert decoded["current_l2"] == 7.5
        assert decoded["current_l3"] == 0
        assert decoded["meter_datetime"] == datetime(2019, 12, 16, 7, 59, 40)
        assert decoded["meter_manufacturer"] == "Aidon"
        assert decoded["reactive_power_export"] == 0
        assert decoded["reactive_power_export_total"] == 5
        assert decoded["reactive_power_export_l1"] == 0
        assert decoded["reactive_power_export_l2"] == 0
        assert decoded["reactive_power_export_l3"] == 0
        assert decoded["reactive_power_import"] == 1507
        assert decoded["reactive_power_import_total"] == 6614347
        assert decoded["reactive_power_import_l1"] == 0
        assert decoded["reactive_power_import_l2"] == 1506
        assert decoded["reactive_power_import_l3"] == 0
        assert decoded["voltage_l1"] == 230.7
        assert decoded["voltage_l2"] == 249.9
        assert decoded["voltage_l3"] == 230.8

    @pytest.mark.parametrize(
        "llc_pdu,notification_body",
        [
            [no_list_1, None],
            [None, bytes.fromhex(NOTIFICATION_BODY_NO_LIST_1)],
        ],
    )
    def test_decode_frame_no_list_1(self, llc_pdu, notification_body):
        """Decode NO list number 1."""
        if llc_pdu is not None:
            decoded = aidon.decode_frame_content(llc_pdu)

        if notification_body is not None:
            decoded = aidon.decode_notification_body(notification_body)

        pprint(decoded)

        assert isinstance(decoded, dict)
        assert len(decoded) == 2
        assert decoded["active_power_import"] == 280
        assert decoded["meter_manufacturer"] == "Aidon"

    @pytest.mark.parametrize(
        "llc_pdu,notification_body",
        [
            [no_list_2, None],
            [None, bytes.fromhex(NOTIFICATION_BODY_NO_LIST_2)],
        ],
    )
    def test_decode_frame_no_list_2(self, llc_pdu, notification_body):
        """Decode NO list number 2."""
        if llc_pdu is not None:
            decoded = aidon.decode_frame_content(llc_pdu)

        if notification_body is not None:
            decoded = aidon.decode_notification_body(notification_body)

        pprint(decoded)

        assert isinstance(decoded, dict)
        assert len(decoded) == 13
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_import"] == 280
        assert decoded["current_l1"] == 1.3
        assert decoded["current_l3"] == 0.9
        assert decoded["list_ver_id"] == "AIDON_V0001"
        assert decoded["meter_id"] == "7359992892587665"
        assert decoded["meter_manufacturer"] == "Aidon"
        assert decoded["meter_type"] == "6525"
        assert decoded["reactive_power_export"] == 128
        assert decoded["reactive_power_import"] == 0
        assert decoded["voltage_l1"] == 227.4
        assert decoded["voltage_l2"] == 230.1
        assert decoded["voltage_l3"] == 230.8

    @pytest.mark.parametrize(
        "llc_pdu,notification_body",
        [
            [no_list_3, None],
            [None, bytes.fromhex(NOTIFICATION_BODY_NO_LIST_3)],
        ],
    )
    def test_decode_frame_no_list_3(self, llc_pdu, notification_body):
        """Decode NO list number 3."""
        if llc_pdu is not None:
            decoded = aidon.decode_frame_content(llc_pdu)

        if notification_body is not None:
            decoded = aidon.decode_notification_body(notification_body)

        pprint(decoded)

        assert isinstance(decoded, dict)
        assert len(decoded) == 18
        assert decoded["active_power_export"] == 0
        assert decoded["active_power_import"] == 280
        assert decoded["active_power_import_total"] == 22721380
        assert decoded["current_l1"] == 1.3
        assert decoded["current_l3"] == 0.9
        assert decoded["list_ver_id"] == "AIDON_V0001"
        assert decoded["meter_datetime"] == datetime(
            2020, 1, 21, 16, 0, tzinfo=timezone.utc
        )
        assert decoded["meter_id"] == "7359992892587665"
        assert decoded["meter_manufacturer"] == "Aidon"
        assert decoded["meter_type"] == "6525"
        assert decoded["reactive_power_export"] == 128
        assert decoded["reactive_power_export_total"] == 1708430.0
        assert decoded["reactive_power_import"] == 0
        assert decoded["reactive_power_import_total"] == 582430.0
        assert decoded["voltage_l1"] == 227.6
        assert decoded["voltage_l2"] == 230.3
        assert decoded["voltage_l3"] == 230.9
