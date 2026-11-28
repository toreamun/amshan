"""Common assertion helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import construct


def assert_llc_pdu(
    container: Any, expected_dsap: int, expected_ssap: int, expected_control: int
) -> None:
    """Assert LLC PDU is as expected."""
    assert container.dsap == expected_dsap
    assert container.ssap == expected_ssap
    assert container.control == expected_control


def assert_long_invokeid_and_priority(
    container: Any,
    expected_invoke_id: int,
    expected_self_descriptive: str,
    expected_processing_option: str,
    expected_service_class: str,
    expected_priority: str,
) -> None:
    """Assert long-invokid-and-priority is as expected."""
    assert isinstance(container, construct.Container)
    assert container.invoke_id == expected_invoke_id
    assert container.self_descriptive == expected_self_descriptive
    assert container.processing_option == expected_processing_option
    assert container.service_class == expected_service_class
    assert container.priority == expected_priority


def assert_obis_element(
    container: Any,
    expected_obis_code: str | None,
    expected_value_type: str,
    expected_value: Any,
) -> None:
    """Assert OBIS element is as expected."""
    assert isinstance(container, construct.Container)
    assert container.obis == expected_obis_code
    assert container.value_type == expected_value_type
    assert container.value == expected_value


def assert_apdu(
    container: Any, expected_invoke_id: int, expected_date_time: datetime | int
) -> None:
    """Assert APDU is as expected."""
    assert_llc_pdu(container, 0xE6, 0xE7, 0x00)
    assert isinstance(container.information, construct.Container)
    assert container.information.Tag == "data_notification"
    assert_long_invokeid_and_priority(
        container.information.LongInvokeIdAndPriority,
        expected_invoke_id,
        "NotSelfDescriptive",
        "ContinueOnError",
        "Unconfirmed",
        "Normal",
    )
    if isinstance(container.information.DateTime, construct.Container):
        assert container.information.DateTime.datetime == expected_date_time
    else:
        assert container.information.DateTime == expected_date_time

    assert isinstance(container.information.notification_body, construct.Container)
