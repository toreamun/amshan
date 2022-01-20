"""Common assertion helpers."""
import construct


def assert_llc_pdu(container, expected_dsap, expected_ssap, expected_control):
    """Assert LLC PDU is as expected."""
    assert container.dsap == expected_dsap
    assert container.ssap == expected_ssap
    assert container.control == expected_control


def assert_long_invokeid_and_priority(
    container,
    expected_invoke_id,
    expected_self_descriptive,
    expected_processing_option,
    expected_service_class,
    expected_priority,
):
    """Assert long-invokid-and-priority is as expected."""
    assert isinstance(container, construct.Container)
    assert container["invoke-id"] == expected_invoke_id
    assert container["self-descriptive"] == expected_self_descriptive
    assert container["processing-option"] == expected_processing_option
    assert container["service-class"] == expected_service_class
    assert container["priority"] == expected_priority


def assert_obis_element(
    container, expected_obis_code, expected_value_type, expected_value
):
    """Assert OBIS element is as expected."""
    assert isinstance(container, construct.Container)
    assert container.obis == expected_obis_code
    assert container.value_type == expected_value_type
    assert container.value == expected_value
