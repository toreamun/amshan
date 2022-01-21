"""Test obis module."""
from amshan.obis import Obis


class TestObis:
    """Test obis class."""

    def test_obis(self):
        """Test from_string, str and eq."""
        obis_code_a = "1.2.3"
        obis_code_a_actual = "0.0.1.2.3.255"
        obis_code_b = "4.5.6"
        obis_a = Obis.from_string(obis_code_a)
        obis_b = Obis.from_string(obis_code_b)

        assert obis_a == obis_code_a
        assert obis_a != obis_b
        assert str(obis_a) == obis_code_a_actual
