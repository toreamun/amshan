"""Autodecoder tests."""
from __future__ import annotations

import pytest

import tests.test_aidon
import tests.test_dlde
import tests.test_kaifa
import tests.test_kamstrup
from han import autodecoder
from han.dlde import DataReadout


@pytest.mark.parametrize(
    "expected_decoder,llc_pdu",
    [
        ["Kamstrup_frame", tests.test_kamstrup.no_list_1_three_phase],
        [
            "Kamstrup_notification_body",
            bytes.fromhex(tests.test_kamstrup.NOTIFICATION_BODY_NO_LIST_1_THREE_PHASE),
        ],
        ["Kamstrup_frame", tests.test_kamstrup.no_list_2_single_phase],
        [
            "Kamstrup_notification_body",
            bytes.fromhex(tests.test_kamstrup.NOTIFICATION_BODY_NO_LIST_2_SINGLE_PHASE),
        ],
        ["Kamstrup_frame", tests.test_kamstrup.no_list_2_three_phase],
        [
            "Kamstrup_notification_body",
            bytes.fromhex(tests.test_kamstrup.NOTIFICATION_BODY_NO_LIST_2_THREE_PHASE),
        ],
        ["Kamstrup_frame", tests.test_kamstrup.no_list_1_single_phase_real_sample],
        [
            "Kamstrup_notification_body",
            bytes.fromhex(
                tests.test_kamstrup.NOTIFICATION_BODY_NO_LIST_1_SINGLE_PHASE_REAL_SAMPLE
            ),
        ],
        ["Kamstrup_frame", tests.test_kamstrup.no_list_2_single_phase_real_sample],
        [
            "Kamstrup_notification_body",
            bytes.fromhex(
                tests.test_kamstrup.NOTIFICATION_BODY_NO_LIST_2_SINGLE_PHASE_REAL_SAMPLE
            ),
        ],
        ["Aidon_frame", tests.test_aidon.no_list_1],
        [
            "Aidon_notification_body",
            bytes.fromhex(tests.test_aidon.NOTIFICATION_BODY_NO_LIST_1),
        ],
        ["Aidon_frame", tests.test_aidon.no_list_2],
        [
            "Aidon_notification_body",
            bytes.fromhex(tests.test_aidon.NOTIFICATION_BODY_NO_LIST_2),
        ],
        ["Aidon_frame", tests.test_aidon.no_list_3],
        [
            "Aidon_notification_body",
            bytes.fromhex(tests.test_aidon.NOTIFICATION_BODY_NO_LIST_3),
        ],
        ["Aidon_frame", tests.test_aidon.se_list],
        [
            "Aidon_notification_body",
            bytes.fromhex(tests.test_aidon.NOTIFICATION_BODY_SE_LIST),
        ],
        ["Kaifa_frame", tests.test_kaifa.no_list_1],
        [
            "Kaifa_notification_body",
            bytes.fromhex(tests.test_kaifa.NOTIFICATION_BODY_NO_LIST_1),
        ],
        ["Kaifa_frame", tests.test_kaifa.no_list_2],
        [
            "Kaifa_notification_body",
            bytes.fromhex(tests.test_kaifa.NOTIFICATION_BODY_NO_LIST_2),
        ],
        ["Kaifa_frame", tests.test_kaifa.no_list_3],
        [
            "Kaifa_notification_body",
            bytes.fromhex(tests.test_kaifa.NOTIFICATION_BODY_NO_LIST_3),
        ],
        ["Kaifa_frame", tests.test_kaifa.se_list],
        [
            "Kaifa_notification_body",
            bytes.fromhex(tests.test_kaifa.NOTIFICATION_BODY_SE_LIST),
        ],
    ],
)
def test_decode_frame(expected_decoder, llc_pdu):
    """Test AutoDecoder."""
    decoder = autodecoder.AutoDecoder()
    assert decoder.previous_success_decoder is None

    decoded = decoder.decode_message_payload(llc_pdu)
    assert decoder.previous_success_decoder == expected_decoder
    assert isinstance(decoded, dict)

    decoded = decoder.decode_message_payload(bytes([1, 2, 3, 4, 5]))
    assert decoded is None
    assert decoder.previous_success_decoder == expected_decoder


def test_decode_message():
    """Test AutoDecoder."""
    decoder = autodecoder.AutoDecoder()
    decoded = decoder.decode_message(
        DataReadout(tests.test_dlde.EXAMPLE_DATA_A_LANDISGYR_360)
    )
    assert decoded
