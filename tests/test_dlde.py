"""Test dllde."""
from datetime import datetime
from pprint import pprint

from amshan.dlde import (
    DataReadout,
    DataSet,
    DataSetValue,
    ModeDReader,
    decode_p1_readout,
    parse_p1_readout,
    parse_p1_readout_content,
)

IDENT = b"/LGF5E360\r\n"
CRLF = b"\r\n"
END_LINE = b"!\r\n"

LINE_WITHOUT_UNIT = b"0-0:1.0.0(210106160710W)\r\n"
LINE_WITH_UNIT = b"1-0:41.7.0(0000.350*kW)\r\n"

# Landis+Gyr E360
EXAMPLE_DATA_A_LANDISGYR_360 = (
    b"/LGF5E360\r\n\r\n"
    b"0-0:1.0.0(210222161900W)\r\n"
    b"1-0:1.8.0(00000896.020*kWh)\r\n"
    b"1-0:2.8.0(00000048.792*kWh)\r\n"
    b"1-0:3.8.0(00000518.309*kVArh)\r\n"
    b"1-0:4.8.0(00000023.732*kVArh)\r\n"
    b"1-0:1.7.0(0000.000*kW)\r\n"
    b"1-0:2.7.0(0000.020*kW)\r\n"
    b"1-0:3.7.0(0000.000*kVAr)\r\n"
    b"1-0:4.7.0(0000.308*kVAr)\r\n"
    b"1-0:21.7.0(0000.000*kW)\r\n"
    b"1-0:22.7.0(0000.012*kW)\r\n"
    b"1-0:41.7.0(0000.000*kW)\r\n"
    b"1-0:42.7.0(0000.071*kW)\r\n"
    b"1-0:61.7.0(0000.063*kW)\r\n"
    b"1-0:62.7.0(0000.000*kW)\r\n"
    b"1-0:23.7.0(0000.000*kVAr)\r\n"
    b"1-0:24.7.0(0000.146*kVAr)\r\n"
    b"1-0:43.7.0(0000.000*kVAr)\r\n"
    b"1-0:44.7.0(0000.135*kVAr)\r\n"
    b"1-0:63.7.0(0000.000*kVAr)\r\n"
    b"1-0:64.7.0(0000.026*kVAr)\r\n"
    b"1-0:32.7.0(230.1*V)\r\n"
    b"1-0:52.7.0(232.2*V)\r\n"
    b"1-0:72.7.0(230.4*V)\r\n"
    b"1-0:31.7.0(000.6*A)\r\n"
    b"1-0:51.7.0(000.6*A)\r\n"
    b"1-0:71.7.0(000.3*A)\r\n"
    b"!A077"
)

EXAMPLE_DATA_B = (
    b"/XMX5LGBBFFB231314239\r\n\r\n"
    b"1-3:0.2.8(42)\r\n"
    b"0-0:1.0.0(180924132132S)\r\n"
    b"0-0:96.1.1(4532323036303137363437393334353135)\r\n"
    b"1-0:1.8.1(011522.839*kWh)\r\n"
    b"1-0:1.8.2(010310.991*kWh)\r\n"
    b"1-0:2.8.1(000000.000*kWh)\r\n"
    b"1-0:2.8.2(000000.000*kWh)\r\n"
    b"0-0:96.14.0(0002)\r\n"
    b"1-0:1.7.0(00.503*kW)\r\n"
    b"1-0:2.7.0(00.000*kW)\r\n"
    b"0-0:96.7.21(00015)\r\n"
    b"0-0:96.7.9(00005)\r\n"
    b"1-0:99.97.0(5)(0-0:96.7.19)(170520130938S)(0000005627*s)(170325044014W)(0043178677*s)\r\n"
    b"1-0:32.32.0(00002)\r\n"
    b"1-0:52.32.0(00002)\r\n"
    b"1-0:72.32.0(00002)\r\n"
    b"1-0:32.36.0(00000)\r\n"
    b"1-0:52.36.0(00000)\r\n"
    b"1-0:72.36.0(00000)\r\n"
    b"0-0:96.13.1()\r\n"
    b"0-0:96.13.0()\r\n"
    b"1-0:31.7.0(001*A)\r\n"
    b"1-0:51.7.0(001*A)\r\n"
    b"1-0:71.7.0(001*A)\r\n"
    b"1-0:21.7.0(00.086*kW)\r\n"
    b"1-0:41.7.0(00.250*kW)\r\n"
    b"1-0:61.7.0(00.166*kW)\r\n"
    b"1-0:22.7.0(00.000*kW)\r\n"
    b"1-0:42.7.0(00.000*kW)\r\n"
    b"1-0:62.7.0(00.000*kW)\r\n"
    b"0-1:24.1.0(003)\r\n"
    b"0-1:96.1.0(4731303138333430313538383732343334)\r\n"
    b"0-1:24.2.1(180924130000S)(04890.857*m3)\r\n"
    b"!\r\n"
)

EXAMPLE_DATA_C = (
    b"/ELL5\\253833635_A\r\n"
    b"\r\n"
    b"0-0:1.0.0(201020085222W)\r\n"
    b"1-0:1.8.0(00001605.055*kWh)\r\n"
    b"1-0:2.8.0(00000000.131*kWh)\r\n"
    b"1-0:3.8.0(00000003.642*kvarh)\r\n"
    b"1-0:4.8.0(00000185.707*kvarh)\r\n"
    b"1-0:1.7.0(0006.000*kW)\r\n"
    b"1-0:2.7.0(0000.000*kW)\r\n"
    b"1-0:3.7.0(0000.200*kvar)\r\n"
    b"1-0:4.7.0(0000.470*kvar)\r\n"
    b"1-0:21.7.0(0003.172*kW)\r\n"
    b"1-0:41.7.0(0000.441*kW)\r\n"
    b"1-0:61.7.0(0002.386*kW)\r\n"
    b"1-0:22.7.0(0000.000*kW)\r\n"
    b"1-0:42.7.0(0000.000*kW)\r\n"
    b"1-0:62.7.0(0000.000*kW)\r\n"
    b"1-0:23.7.0(0000.000*kvar)\r\n"
    b"1-0:43.7.0(0000.200*kvar)\r\n"
    b"1-0:63.7.0(0000.000*kvar)\r\n"
    b"1-0:24.7.0(0000.222*kvar)\r\n"
    b"1-0:44.7.0(0000.000*kvar)\r\n"
    b"1-0:64.7.0(0000.247*kvar)\r\n"
    b"1-0:32.7.0(234.4*V)\r\n"
    b"1-0:52.7.0(233.3*V)\r\n"
    b"1-0:72.7.0(235.1*V)\r\n"
    b"1-0:31.7.0(013.6*A)\r\n"
    b"1-0:51.7.0(002.0*A)\r\n"
    b"1-0:71.7.0(010.2*A)\r\n"
    b"!80FF\r\n"
)

# Landis+Gyr E360
EXAMPLE_DATA_D_LANDISGYR_360 = (
    b"/LGF5E360\r\n"
    b"\r\n"
    b"0-0:1.0.0(220204110650W)\r\n"
    b"1-0:1.8.0(00010501.076*kWh)\r\n"
    b"1-0:2.8.0(00000000.000*kWh)\r\n"
    b"1-0:3.8.0(00001761.087*kVArh)\r\n"
    b"1-0:4.8.0(00000008.391*kVArh)\r\n"
    b"1-0:1.7.0(0002.301*kW)\r\n"
    b"1-0:2.7.0(0000.000*kW)\r\n"
    b"1-0:3.7.0(0000.135*kVAr)\r\n"
    b"1-0:4.7.0(0000.000*kVAr)\r\n"
    b"1-0:21.7.0(0000.622*kW)\r\n"
    b"1-0:22.7.0(0000.000*kW)\r\n"
    b"1-0:41.7.0(0000.667*kW)\r\n"
    b"1-0:42.7.0(0000.000*kW)\r\n"
    b"1-0:61.7.0(0001.011*kW)\r\n"
    b"1-0:62.7.0(0000.000*kW)\r\n"
    b"1-0:23.7.0(0000.000*kVAr)\r\n"
    b"1-0:24.7.0(0000.208*kVAr)\r\n"
    b"1-0:43.7.0(0000.000*kVAr)\r\n"
    b"1-0:44.7.0(0000.142*kVAr)\r\n"
    b"1-0:63.7.0(0000.486*kVAr)\r\n"
    b"1-0:64.7.0(0000.000*kVAr)\r\n"
    b"1-0:32.7.0(232.1*V)\r\n"
    b"1-0:52.7.0(233.1*V)\r\n"
    b"1-0:72.7.0(231.9*V)\r\n"
    b"1-0:31.7.0(002.8*A)\r\n"
    b"1-0:51.7.0(002.9*A)\r\n"
    b"1-0:71.7.0(004.8*A)\r\n"
    b"!8012\r\n"
)


class TestModeDReader:
    """Test Mode D reader."""

    def test_incomplete(self):
        """Incomplete message should return empty."""
        reader = ModeDReader()
        assert len(reader.read(IDENT)) == 0
        assert len(reader.read(LINE_WITHOUT_UNIT)) == 0

    def test_read_item_without_unit(self):
        """Test read item without unit."""
        reader = ModeDReader()

        assert len(reader.read(IDENT)) == 0
        assert len(reader.read(CRLF)) == 0
        assert len(reader.read(LINE_WITHOUT_UNIT)) == 0
        readouts = reader.read(END_LINE)
        assert len(readouts) == 1
        assert readouts[0].as_bytes == (IDENT + CRLF + LINE_WITHOUT_UNIT + END_LINE)
        assert str(readouts[0].identification_line) == IDENT.decode("ascii").strip()
        assert readouts[0].end_line == END_LINE.decode("ascii").strip()
        assert readouts[0].payload == (CRLF + LINE_WITHOUT_UNIT)
        assert readouts[0].is_valid

        items = parse_p1_readout(readouts[0])
        pprint(items)
        assert items[0] == DataSet(
            address="0-0:1.0.0", values=[DataSetValue(value="210106160710W", unit=None)]
        )

    def test_read_item_with_unit(self):
        """Test read item without unit."""
        reader = ModeDReader()
        readout_data = IDENT + CRLF + LINE_WITHOUT_UNIT + LINE_WITH_UNIT + END_LINE
        readouts = reader.read(readout_data)
        items = parse_p1_readout(readouts[0])
        pprint(items)
        assert items[1] == DataSet(
            address="1-0:41.7.0", values=[DataSetValue(value="0000.350", unit="kW")]
        )


class TestDataReadout:
    """Test DataReadout."""

    def test_example_a_landisgyr_360(self):
        """Load example data A Landis+Gyr 360."""
        readout = DataReadout(EXAMPLE_DATA_A_LANDISGYR_360)
        assert readout.identification_line
        assert str(readout.identification_line) == "/LGF5E360"
        assert readout.end_line == "!A077"
        assert readout.expected_checksum == 0xA077
        assert readout._calculated_crc == 0xA077  # pylint: disable=protected-access
        assert readout.is_valid

    def test_example_b(self):
        """Load example data B."""
        readout = DataReadout(EXAMPLE_DATA_B)
        assert readout.identification_line
        assert str(readout.identification_line) == "/XMX5LGBBFFB231314239"
        assert readout.end_line == "!"

    def test_example_c(self):
        """Load example data C."""
        readout = DataReadout(EXAMPLE_DATA_C)
        assert readout.identification_line
        assert str(readout.identification_line) == "/ELL5\\253833635_A"
        assert readout.end_line == "!80FF"
        assert readout.expected_checksum == 0x80FF
        assert readout._calculated_crc == 0x80FF  # pylint: disable=protected-access
        assert readout.is_valid

    def test_example_d_landisgyr_360(self):
        """Load example data D Landis+Gyr E360."""
        readout = DataReadout(EXAMPLE_DATA_D_LANDISGYR_360)
        assert readout.identification_line
        assert str(readout.identification_line) == "/LGF5E360"
        assert readout.end_line == "!8012"
        assert readout.expected_checksum == 0x8012
        assert readout._calculated_crc == 0x8012  # pylint: disable=protected-access
        assert readout.is_valid


class TestParse:
    """Test parse P1 readouts."""

    def test_parse_junk(self):
        """Assert that parsing junk data return empty."""
        junk = bytes([1, 2, 3, 4, 5])
        parsed = parse_p1_readout_content(junk)
        assert len(parsed) == 0

    def test_parse_example_a_landisgyr_360(self):
        """Parse example data A Landis+Gyr 360."""
        parsed = parse_p1_readout(DataReadout(EXAMPLE_DATA_A_LANDISGYR_360))
        pprint(parsed)
        assert parsed[0] == DataSet(
            address="0-0:1.0.0",
            values=[DataSetValue(value="210222161900W", unit=None)],
        )

        assert parsed[1] == DataSet(
            address="1-0:1.8.0", values=[DataSetValue(value="00000896.020", unit="kWh")]
        )
        assert parsed[2] == DataSet(
            address="1-0:2.8.0", values=[DataSetValue(value="00000048.792", unit="kWh")]
        )
        assert parsed[3] == DataSet(
            address="1-0:3.8.0",
            values=[DataSetValue(value="00000518.309", unit="kVArh")],
        )
        assert parsed[4] == DataSet(
            address="1-0:4.8.0",
            values=[DataSetValue(value="00000023.732", unit="kVArh")],
        )
        assert parsed[5] == DataSet(
            address="1-0:1.7.0", values=[DataSetValue(value="0000.000", unit="kW")]
        )
        assert parsed[6] == DataSet(
            address="1-0:2.7.0", values=[DataSetValue(value="0000.020", unit="kW")]
        )
        assert parsed[7] == DataSet(
            address="1-0:3.7.0", values=[DataSetValue(value="0000.000", unit="kVAr")]
        )
        assert parsed[8] == DataSet(
            address="1-0:4.7.0", values=[DataSetValue(value="0000.308", unit="kVAr")]
        )
        assert parsed[9] == DataSet(
            address="1-0:21.7.0", values=[DataSetValue(value="0000.000", unit="kW")]
        )
        assert parsed[10] == DataSet(
            address="1-0:22.7.0", values=[DataSetValue(value="0000.012", unit="kW")]
        )
        assert parsed[11] == DataSet(
            address="1-0:41.7.0", values=[DataSetValue(value="0000.000", unit="kW")]
        )
        assert parsed[12] == DataSet(
            address="1-0:42.7.0", values=[DataSetValue(value="0000.071", unit="kW")]
        )
        assert parsed[13] == DataSet(
            address="1-0:61.7.0", values=[DataSetValue(value="0000.063", unit="kW")]
        )
        assert parsed[14] == DataSet(
            address="1-0:62.7.0", values=[DataSetValue(value="0000.000", unit="kW")]
        )
        assert parsed[15] == DataSet(
            address="1-0:23.7.0", values=[DataSetValue(value="0000.000", unit="kVAr")]
        )
        assert parsed[16] == DataSet(
            address="1-0:24.7.0", values=[DataSetValue(value="0000.146", unit="kVAr")]
        )
        assert parsed[17] == DataSet(
            address="1-0:43.7.0", values=[DataSetValue(value="0000.000", unit="kVAr")]
        )
        assert parsed[18] == DataSet(
            address="1-0:44.7.0", values=[DataSetValue(value="0000.135", unit="kVAr")]
        )
        assert parsed[19] == DataSet(
            address="1-0:63.7.0", values=[DataSetValue(value="0000.000", unit="kVAr")]
        )
        assert parsed[20] == DataSet(
            address="1-0:64.7.0", values=[DataSetValue(value="0000.026", unit="kVAr")]
        )
        assert parsed[21] == DataSet(
            address="1-0:32.7.0", values=[DataSetValue(value="230.1", unit="V")]
        )
        assert parsed[22] == DataSet(
            address="1-0:52.7.0", values=[DataSetValue(value="232.2", unit="V")]
        )
        assert parsed[23] == DataSet(
            address="1-0:72.7.0", values=[DataSetValue(value="230.4", unit="V")]
        )
        assert parsed[24] == DataSet(
            address="1-0:31.7.0", values=[DataSetValue(value="000.6", unit="A")]
        )
        assert parsed[25] == DataSet(
            address="1-0:51.7.0", values=[DataSetValue(value="000.6", unit="A")]
        )
        assert parsed[26] == DataSet(
            address="1-0:71.7.0", values=[DataSetValue(value="000.3", unit="A")]
        )

    def test_parse_multi_value_line(self):
        """Parse data block line of single data set and multiple values."""
        data_block = b"1-0:99.97.0(5)(0-0:96.7.19)(170520130938S)(0000005627*s)(170325044014W)(0043178677*s)\r\n"
        parsed = parse_p1_readout_content(data_block)
        pprint(parsed)
        assert parsed == [
            DataSet(
                address="1-0:99.97.0",
                values=[
                    DataSetValue(value="5", unit=None),
                    DataSetValue(value="0-0:96.7.19", unit=None),
                    DataSetValue(value="170520130938S", unit=None),
                    DataSetValue(value="0000005627", unit="s"),
                    DataSetValue(value="170325044014W", unit=None),
                    DataSetValue(value="0043178677", unit="s"),
                ],
            ),
        ]

    def test_parse_multi_dataset_line(self):
        """Parse data block line of multiple data set and multiple values."""
        data_block = (
            b"1-0:99.97.0(5)(0-0:96.7.19)(170520130938S)(0000005627*s)(170325044014W)(0043178677*s)"
            b"0-0:1.0.0(180924132132S)"
        )
        parsed = parse_p1_readout_content(data_block)
        pprint(parsed)
        assert parsed == [
            DataSet(
                address="1-0:99.97.0",
                values=[
                    DataSetValue(value="5", unit=None),
                    DataSetValue(value="0-0:96.7.19", unit=None),
                    DataSetValue(value="170520130938S", unit=None),
                    DataSetValue(value="0000005627", unit="s"),
                    DataSetValue(value="170325044014W", unit=None),
                    DataSetValue(value="0043178677", unit="s"),
                ],
            ),
            DataSet(
                address="0-0:1.0.0",
                values=[DataSetValue(value="180924132132S", unit=None)],
            ),
        ]


class TestDecode:
    """Test decode P1 readouts."""

    def test_decode_example(self):
        """Decode example data."""
        decoded = decode_p1_readout(DataReadout(EXAMPLE_DATA_D_LANDISGYR_360))
        pprint(decoded)
        expected = {
            "active_power_export": 0,
            "active_power_export_l1": 0,
            "active_power_export_l2": 0,
            "active_power_export_l3": 0,
            "active_power_export_total": 0,
            "active_power_import": 2301,
            "active_power_import_l1": 622,
            "active_power_import_l2": 667,
            "active_power_import_l3": 1010,
            "active_power_import_total": 10501076,
            "current_l1": 2.8,
            "current_l2": 2.9,
            "current_l3": 4.8,
            "meter_datetime": datetime(2022, 2, 4, 11, 6, 50),
            "meter_manufacturer_id": "LGF",
            "meter_type_id": "E360",
            "reactive_power_export": 0,
            "reactive_power_export_l1": 208,
            "reactive_power_export_l2": 142,
            "reactive_power_export_l3": 0,
            "reactive_power_export_total": 8391,
            "reactive_power_import": 135,
            "reactive_power_import_l1": 0,
            "reactive_power_import_l2": 0,
            "reactive_power_import_l3": 486,
            "reactive_power_import_total": 1761087,
            "voltage_l1": 232.1,
            "voltage_l2": 233.1,
            "voltage_l3": 231.9,
        }
        assert decoded == expected
