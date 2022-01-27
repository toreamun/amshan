"""Test obis module."""
from __future__ import annotations
from amshan.obis import OBIS_CODES, Obis, to_obis_tupple
from amshan.obis_map import (
    FIELD_METER_DATETIME,
    FIELD_METER_ID,
    FIELD_METER_TYPE,
    FIELD_OBIS_LIST_VER_ID,
    name_obis_map,
)


class TestObis:
    """Test obis class."""

    def test_obis(self):
        """Test from_string, str and eq."""
        obis_code_a = "1.2.3"
        obis_code_b = "4.5.6"
        obis_a = Obis.from_string(obis_code_a)
        obis_b = Obis.from_string(obis_code_b)

        assert obis_a == obis_code_a
        assert obis_a != obis_b

    def test_all_from_obis_map_in_obis_codes(self):
        """Assert that all required obis codes from obis_map in OBIS_CODES."""
        remove = [
            FIELD_OBIS_LIST_VER_ID,
            FIELD_METER_ID,
            FIELD_METER_TYPE,
            FIELD_METER_DATETIME,
        ]
        expected = [val for key, val in name_obis_map.items() if key not in remove]
        expected_obis_codes = []
        for obis_values in expected:
            expected_obis_codes.extend(obis_values)

        defined = {x.code.to_group_cdr_str() for x in OBIS_CODES}

        for code in expected_obis_codes:
            assert code in defined


class TestToTupple:
    """Test obis-to-tupple parsing."""

    def test_reduced(self):
        """Assert that reduced codes parse correctly."""
        assert to_obis_tupple("3.4") == (None, None, 3, 4, None, None)
        assert to_obis_tupple("3.4.5") == (None, None, 3, 4, 5, None)
        assert to_obis_tupple("2:3.4.5") == (None, 2, 3, 4, 5, None)
        assert to_obis_tupple("1-3.4.5") == (1, None, 3, 4, 5, None)
        assert to_obis_tupple("3.4*6") == (None, None, 3, 4, None, 6)
        assert to_obis_tupple("1-2:3.4*6") == (1, 2, 3, 4, None, 6)
        assert to_obis_tupple("1-2:3.4.5*6") == (1, 2, 3, 4, 5, 6)

    def test_standard(self):
        """Assert that standard codes parse correctly."""
        assert to_obis_tupple("1.2.3.4.5.6") == (1, 2, 3, 4, 5, 6)
