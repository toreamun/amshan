"""Test dllde."""
from datetime import datetime
from pprint import pprint
from amshan.dlde import DataReadout, ModeDReader, decode_p1_readout, parse_p1_readout

IDENT = b"/LGF5E360\r\n"
CRLF = b"\r\n"
END_LINE = b"!A7AF\r\n"

LINE_WITHOUT_UNIT = b"0-0:1.0.0(210106160710W)\r\n"
LINE_WITH_UNIT = b"1-0:41.7.0(0000.350*kW)\r\n"

EXAMPLE_DATA = (
    b"/ELL5\x5c253833635_A\r\n\r\n"
    b"0-0:1.0.0(210217184019W)\r\n"
    b"1-0:1.8.0(00006678.394*kWh)\r\n"
    b"1-0:2.8.0(00000000.000*kWh)\r\n"
    b"1-0:3.8.0(00000021.988*kvarh)\r\n"
    b"1-0:4.8.0(00001020.971*kvarh)\r\n"
    b"1-0:1.7.0(0001.727*kW)\r\n"
    b"1-0:2.7.0(0000.000*kW)\r\n"
    b"1-0:3.7.0(0000.000*kvar)\r\n"
    b"1-0:4.7.0(0000.309*kvar)\r\n"
    b"1-0:21.7.0(0001.023*kW)\r\n"
    b"1-0:41.7.0(0000.350*kW)\r\n"
    b"1-0:61.7.0(0000.353*kW)\r\n"
    b"1-0:22.7.0(0000.000*kW)\r\n"
    b"1-0:42.7.0(0000.000*kW)\r\n"
    b"1-0:62.7.0(0000.000*kW)\r\n"
    b"1-0:23.7.0(0000.000*kvar)\r\n"
    b"1-0:43.7.0(0000.000*kvar)\r\n"
    b"1-0:63.7.0(0000.000*kvar)\r\n"
    b"1-0:24.7.0(0000.009*kvar)\r\n"
    b"1-0:44.7.0(0000.161*kvar)\r\n"
    b"1-0:64.7.0(0000.138*kvar)\r\n"
    b"1-0:32.7.0(240.3*V)\r\n"
    b"1-0:52.7.0(240.1*V)\r\n"
    b"1-0:72.7.0(241.3*V)\r\n"
    b"1-0:31.7.0(004.2*A)\r\n"
    b"1-0:51.7.0(001.6*A)\r\n"
    b"1-0:71.7.0(001.7*A)\r\n!"
)


class TestModeDReader:
    """Test Mode D reader."""

    def test_incomplete(self) -> None:
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
        assert readouts[0].readout_bytes == (
            IDENT + CRLF + LINE_WITHOUT_UNIT + END_LINE
        )
        assert readouts[0].identification_line == IDENT.decode("ascii").strip()
        assert readouts[0].end_line == END_LINE.decode("ascii").strip()

        items = parse_p1_readout(readouts[0])
        pprint(items)
        assert items[0] == ("0-0:1.0.0", "210106160710W", None)

    def test_read_item_with_unit(self):
        """Test read item without unit."""
        reader = ModeDReader()
        readout_data = IDENT + CRLF + LINE_WITHOUT_UNIT + LINE_WITH_UNIT + END_LINE
        readouts = reader.read(readout_data)
        items = parse_p1_readout(readouts[0])
        pprint(items)
        assert items[1] == ("1-0:41.7.0", "0000.350", "kW")


class TestParse:
    """Test parse P1 readouts."""

    def test_parse_example(self):
        """Parse example data."""
        parsed = parse_p1_readout(DataReadout(EXAMPLE_DATA))
        pprint(parsed)
        assert parsed[0] == ("0-0:1.0.0", "210217184019W", None)
        assert parsed[1] == ("1-0:1.8.0", "00006678.394", "kWh")
        assert parsed[2] == ("1-0:2.8.0", "00000000.000", "kWh")
        assert parsed[3] == ("1-0:3.8.0", "00000021.988", "kvarh")
        assert parsed[4] == ("1-0:4.8.0", "00001020.971", "kvarh")
        assert parsed[5] == ("1-0:1.7.0", "0001.727", "kW")
        assert parsed[6] == ("1-0:2.7.0", "0000.000", "kW")
        assert parsed[7] == ("1-0:3.7.0", "0000.000", "kvar")
        assert parsed[8] == ("1-0:4.7.0", "0000.309", "kvar")
        assert parsed[9] == ("1-0:21.7.0", "0001.023", "kW")
        assert parsed[10] == ("1-0:41.7.0", "0000.350", "kW")
        assert parsed[11] == ("1-0:61.7.0", "0000.353", "kW")
        assert parsed[12] == ("1-0:22.7.0", "0000.000", "kW")
        assert parsed[13] == ("1-0:42.7.0", "0000.000", "kW")
        assert parsed[14] == ("1-0:62.7.0", "0000.000", "kW")
        assert parsed[15] == ("1-0:23.7.0", "0000.000", "kvar")
        assert parsed[16] == ("1-0:43.7.0", "0000.000", "kvar")
        assert parsed[17] == ("1-0:63.7.0", "0000.000", "kvar")
        assert parsed[18] == ("1-0:24.7.0", "0000.009", "kvar")
        assert parsed[19] == ("1-0:44.7.0", "0000.161", "kvar")
        assert parsed[20] == ("1-0:64.7.0", "0000.138", "kvar")
        assert parsed[21] == ("1-0:32.7.0", "240.3", "V")
        assert parsed[22] == ("1-0:52.7.0", "240.1", "V")
        assert parsed[23] == ("1-0:72.7.0", "241.3", "V")
        assert parsed[24] == ("1-0:31.7.0", "004.2", "A")
        assert parsed[25] == ("1-0:51.7.0", "001.6", "A")
        assert parsed[26] == ("1-0:71.7.0", "001.7", "A")

    def test_decode_example(self):
        """Decode example data."""
        decoded = decode_p1_readout(DataReadout(EXAMPLE_DATA))
        pprint(decoded)
        assert decoded == {
            "1.0.0": datetime(2021, 2, 17, 18, 40, 19),
            "1.7.0": 1.727,
            "1.8.0": 6678.394,
            "2.7.0": 0.0,
            "2.8.0": 0.0,
            "21.7.0": 1.023,
            "22.7.0": 0.0,
            "23.7.0": 0.0,
            "24.7.0": 0.009,
            "3.7.0": 0.0,
            "3.8.0": 21.988,
            "31.7.0": 4.2,
            "32.7.0": 240.3,
            "4.7.0": 0.309,
            "4.8.0": 1020.971,
            "41.7.0": 0.35,
            "42.7.0": 0.0,
            "43.7.0": 0.0,
            "44.7.0": 0.161,
            "51.7.0": 1.6,
            "52.7.0": 240.1,
            "61.7.0": 0.353,
            "62.7.0": 0.0,
            "63.7.0": 0.0,
            "64.7.0": 0.138,
            "71.7.0": 1.7,
            "72.7.0": 241.3,
        }
