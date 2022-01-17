"""Kamstrup tests."""
# pylint: disable = no-self-use
from datetime import datetime
from pprint import pprint

import construct

from amshan import kamstrup

# Kamstrup example 1: 10 seconds list, three-phases, four-quadrants
list_1_three_phase = bytes.fromhex(
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
list_2_single_phase = bytes.fromhex(
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
        "0906 0001010000FF"  # octet_string (obis)
        "090C 07E1081003100005FF800000"  # octet_string
        "0906 0101010800FF0600000000"  # octet_string
    ).replace(" ", "")
)

# Kamstrup example 2: 1 hour list, three-phases, four-quadrants
list_2_three_phase = bytes.fromhex(
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
        "0906 0001010000FF"  # octet_string
        "090C 07E1081003100005FF800000"
        "0906 0101010800FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101020800FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101030800FF  06 00000000"  # octet_string (obis) + double_long_unsigned
        "0906 0101040800FF  06 00000000"  # octet_string (obis) + double_long_unsigned
    ).replace(" ", "")
)

list_1_single_phase_real_sample = bytes.fromhex(
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

list_2_single_phase_real_sample = bytes.fromhex(
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
        "0906 0001010000ff"
        "090c 07e50b1803000019ff800000"
        "0906 0101010800ff  06 00762ee2"
        "0906 0101020800ff  06 00000000"
        "0906 0101030800ff  06 000035a3"
        "0906 0101040800ff  06 00116b53"
    ).replace(" ", "")
)


def _assert_llc_pdu(container, expected_dsap, expected_ssap, expected_control):
    assert container.dsap == expected_dsap
    assert container.ssap == expected_ssap
    assert container.control == expected_control


def _assert_long_invokeid_and_priority(
    container,
    expected_invoke_id,
    expected_self_descriptive,
    expected_processing_option,
    expected_service_class,
    expected_priority,
):
    assert isinstance(container, construct.Container)
    assert container["invoke-id"] == expected_invoke_id
    assert container["self-descriptive"] == expected_self_descriptive
    assert container["processing-option"] == expected_processing_option
    assert container["service-class"] == expected_service_class
    assert container["priority"] == expected_priority


def _assert_obis_element(
    container, expected_obis_code, expected_value_type, expected_value
):
    assert isinstance(container, construct.Container)
    assert container.obis == expected_obis_code
    assert container.value_type == expected_value_type
    assert container.value == expected_value


class TestParseKamstrup:
    """Test parse Kamstrup frames."""

    def test_parse_list_1_single_phase_real_sample(self):
        """Parse single phase list number 1."""
        parsed = kamstrup.LlcPdu.parse(list_1_single_phase_real_sample)

        print(parsed)

        assert isinstance(parsed, construct.Container)
        _assert_llc_pdu(parsed, 0xE6, 0xE7, 0x00)

        assert isinstance(parsed.information, construct.Container)
        assert parsed.information.Tag == 0x0F

        _assert_long_invokeid_and_priority(
            parsed.information.LongInvokeIdAndPriority,
            0,
            "NotSelfDescriptive",
            "ContinueOnError",
            "Unconfirmed",
            "Normal",
        )

        assert isinstance(parsed.information.DateTime, construct.Container)
        assert parsed.information.DateTime.datetime == datetime(2022, 1, 17, 12, 44, 40)

        assert isinstance(parsed.information.notification_body, construct.Container)
        assert parsed.information.notification_body.length == 0x19

        assert isinstance(
            parsed.information.notification_body.list_items, construct.ListContainer
        )

        _assert_obis_element(
            parsed.information.notification_body.list_items[0],
            None,
            "visible_string",
            "Kamstrup_V0001",
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[1],
            "1.1.0.0.5.255",  # GS1 number
            "visible_string",
            "5705705705705702",
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[2],
            "1.1.96.1.1.255",  # Meter type
            "visible_string",
            "6861111BN242101040",
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[3],
            "1.1.1.7.0.255",  # P14
            "double_long_unsigned",
            1896,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[4],
            "1.1.2.7.0.255",  # P23
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[5],
            "1.1.3.7.0.255",  # Q12
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[6],
            "1.1.4.7.0.255",  # Q34
            "double_long_unsigned",
            493,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[7],
            "1.1.31.7.0.255",  # IL1
            "double_long_unsigned",
            896,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[8],
            "1.1.32.7.0.255",  # UL1
            "long_unsigned",
            225,
        )

    def test_parse_list_2_single_phase_real_sample(self):
        """Parse single phase list number 1."""
        parsed = kamstrup.LlcPdu.parse(list_2_single_phase_real_sample)

        print(parsed)

        assert isinstance(parsed, construct.Container)
        _assert_llc_pdu(parsed, 0xE6, 0xE7, 0x00)

        assert isinstance(parsed.information, construct.Container)
        assert parsed.information.Tag == 0x0F

        _assert_long_invokeid_and_priority(
            parsed.information.LongInvokeIdAndPriority,
            0,
            "NotSelfDescriptive",
            "ContinueOnError",
            "Unconfirmed",
            "Normal",
        )

        assert isinstance(parsed.information.DateTime, construct.Container)
        assert parsed.information.DateTime.datetime == datetime(2021, 11, 24, 0, 0, 25)

        assert isinstance(parsed.information.notification_body, construct.Container)
        assert parsed.information.notification_body.length == 0x23

        assert isinstance(
            parsed.information.notification_body.list_items, construct.ListContainer
        )

        _assert_obis_element(
            parsed.information.notification_body.list_items[0],
            None,
            "visible_string",
            "Kamstrup_V0001",
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[1],
            "1.1.0.0.5.255",  # GS1 number
            "visible_string",
            "5705705705705702",
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[2],
            "1.1.96.1.1.255",  # Meter type
            "visible_string",
            "6861111BN242101040",
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[3],
            "1.1.1.7.0.255",  # P14
            "double_long_unsigned",
            10050,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[4],
            "1.1.2.7.0.255",  # P23
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[5],
            "1.1.3.7.0.255",  # Q12
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[6],
            "1.1.4.7.0.255",  # Q34
            "double_long_unsigned",
            279,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[7],
            "1.1.31.7.0.255",  # IL1
            "double_long_unsigned",
            4512,
        )
        _assert_obis_element(
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

        _assert_obis_element(
            parsed.information.notification_body.list_items[10],
            "1.1.1.8.0.255",  # A14
            "double_long_unsigned",
            7745250,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[11],
            "1.1.2.8.0.255",  # A23
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[12],
            "1.1.3.8.0.255",  # R12
            "double_long_unsigned",
            13731,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[13],
            "1.1.4.8.0.255",  # R12
            "double_long_unsigned",
            1141587,
        )

    def test_parse_list_1_three_phase(self):
        """Parse three phase list number 1."""
        parsed = kamstrup.LlcPdu.parse(list_1_three_phase)

        print(parsed)

        assert isinstance(parsed, construct.Container)
        _assert_llc_pdu(parsed, 0xE6, 0xE7, 0x00)

        assert isinstance(parsed.information, construct.Container)
        assert parsed.information.Tag == 0x0F

        _assert_long_invokeid_and_priority(
            parsed.information.LongInvokeIdAndPriority,
            0,
            "NotSelfDescriptive",
            "ContinueOnError",
            "Unconfirmed",
            "Normal",
        )

        assert isinstance(parsed.information.DateTime, construct.Container)
        assert parsed.information.DateTime.datetime == datetime(2000, 1, 1, 22, 33, 0)

        assert isinstance(parsed.information.notification_body, construct.Container)
        assert parsed.information.notification_body.length == 0x19

        assert isinstance(
            parsed.information.notification_body.list_items, construct.ListContainer
        )

        _assert_obis_element(
            parsed.information.notification_body.list_items[0],
            None,
            "visible_string",
            "Kamstrup_V0001",
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[1],
            "1.1.0.0.5.255",  # GS1 number
            "visible_string",
            "5706567000000000",
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[2],
            "1.1.96.1.1.255",  # Meter type
            "visible_string",
            "000000000000000000",
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[3],
            "1.1.1.7.0.255",  # P14
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[4],
            "1.1.2.7.0.255",  # P23
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[5],
            "1.1.3.7.0.255",  # Q12
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[6],
            "1.1.4.7.0.255",  # Q34
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[7],
            "1.1.31.7.0.255",  # IL1
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[8],
            "1.1.51.7.0.255",  # IL2
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[9],
            "1.1.71.7.0.255",  # IL3
            "double_long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[10],
            "1.1.32.7.0.255",  # UL1
            "long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[11],
            "1.1.52.7.0.255",  # UL2
            "long_unsigned",
            0,
        )
        _assert_obis_element(
            parsed.information.notification_body.list_items[12],
            "1.1.72.7.0.255",  # UL3
            "long_unsigned",
            0,
        )

    def test_parse_list_2_single_phase(self):
        """Parse single phase list number 2."""
        parsed = kamstrup.LlcPdu.parse(list_2_single_phase)
        assert isinstance(parsed, construct.Container)
        print(parsed)

    def test_parse_list_2_three_phase(self):
        """Parse three phase list number 2."""
        parsed = kamstrup.LlcPdu.parse(list_2_three_phase)
        assert isinstance(parsed, construct.Container)
        print(parsed)


class TestDecodeKamstrup:
    """Test decode Kamstrup frames."""

    def test_decode_frame_list_1_single_phase_real_sample(self):
        """Decode three phase list number 1."""
        decoded = kamstrup.decode_frame_content(list_1_single_phase_real_sample)
        assert isinstance(decoded, dict)
        pprint(decoded)

    def test_decode_frame_list_2_single_phase_real_sample(self):
        """Decode three phase list number 1."""
        decoded = kamstrup.decode_frame_content(list_2_single_phase_real_sample)
        assert isinstance(decoded, dict)
        pprint(decoded)

    def test_decode_frame_list_1_three_phase(self):
        """Decode three phase list number 1."""
        decoded = kamstrup.decode_frame_content(list_1_three_phase)
        assert isinstance(decoded, dict)
        pprint(decoded)

    def test_decode_frame_list_2_three_phase(self):
        """Decode three phase list number 2."""
        decoded = kamstrup.decode_frame_content(list_2_three_phase)
        assert isinstance(decoded, dict)
        pprint(decoded)

    def test_decode_frame_list_2_single_phase(self):
        """Decode single phase list number 2."""
        decoded = kamstrup.decode_frame_content(list_2_single_phase)
        assert isinstance(decoded, dict)
        pprint(decoded)
