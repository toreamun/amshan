import logging
from pprint import pprint

import construct

from smartmeterdecode import kaifa

logging.basicConfig(level=logging.DEBUG)

list_1 = bytes.fromhex(
    "e6e700" "0f" "40000000" "090c07e3020401173416ff800000" "0201" "06000016dc"
)

list_2 = bytes.fromhex(
    "e6e700"
    "0f"
    "40000000"
    "090c07e40119060d091eff800000"
    "020d"
    "09074b464d5f303031"
    "091036393730363331343032363134343736"
    "09084d413330344833450600002611"
    "0600000000"
    "0600000000"
    "06000001b3"
    "0600008415"
    "0600006dc7"
    "0600004702"
    "0600000878"
    "0600000000"
    "060000088c"
)

list_3 = bytes.fromhex(
    "e6e700"
    "0f"
    "40000000"
    "090c07e40119060e000aff800000"
    "0212"
    "09074b464d5f303031"
    "091036393730363331343032363134343736"
    "09084d41333034483345"
    "0600001328"
    "0600000000"
    "0600000000"
    "0600000179"
    "06000038eb"
    "0600003d1b"
    "0600002535"
    "0600000891"
    "0600000000"
    "060000089d"
    "090c07e40119060e000aff800000"
    "0604be76e80600000000"
    "06000d922d060030feb4"
)


class TestParseKaifa:
    def test_parse_list_1(self):
        parsed = kaifa.LlcPdu.parse(list_1)
        assert isinstance(parsed, construct.Container)
        print(parsed)

    def test_parse_list_2(self):
        parsed = kaifa.LlcPdu.parse(list_2)
        assert isinstance(parsed, construct.Container)
        print(parsed)

    def test_parse_list_3(self):
        parsed = kaifa.LlcPdu.parse(list_3)
        assert isinstance(parsed, construct.Container)
        print(parsed)


class TestDecodeKaifa:
    def test_decode_frame_list_1(self):
        decoded = kaifa.decode_frame(list_1)
        assert isinstance(decoded, dict)
        pprint(decoded)

    def test_decode_frame_list_2(self):
        decoded = kaifa.decode_frame(list_2)
        assert isinstance(decoded, dict)
        pprint(decoded)

    def test_decode_frame_list_3(self):
        decoded = kaifa.decode_frame(list_3)
        assert isinstance(decoded, dict)
        pprint(decoded)
