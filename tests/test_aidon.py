from pprint import pprint

import construct

from meterdecode import aidon

list_1 = bytes.fromhex(
    "e6e700"
    "0f"
    "40000000"
    "00"
    "0101"
    "020309060100010700ff060000011802020f00161b")

list_2 = bytes.fromhex(
    "e6e700"
    "0f"
    "40000000"
    "00"
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
    "020309060100480700ff12090402020fff1623")

list_3 = bytes.fromhex(
    "e6e700"
    "0f"
    "40000000"
    "00"
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
    "02020f011620")


class TestParseAidon:

    def test_decode_list_1(self):
        parsed = aidon.LlcPdu.parse(list_1)
        assert isinstance(parsed, construct.Container)
        print(parsed)

    def test_decode_list_2(self):
        parsed = aidon.LlcPdu.parse(list_2)
        assert isinstance(parsed, construct.Container)
        print(parsed)

    def test_decode_list_3(self):
        parsed = aidon.LlcPdu.parse(list_3)
        assert isinstance(parsed, construct.Container)
        print(parsed)


class TestDecodeAidon:

    def test_decode_frame_list_1(self):
        decoded = aidon.decode_frame(list_1)
        assert isinstance(decoded, dict)
        pprint(decoded)

    def test_decode_frame_list_2(self):
        decoded = aidon.decode_frame(list_2)
        assert isinstance(decoded, dict)
        pprint(decoded)

    def test_decode_frame_list_3(self):
        decoded = aidon.decode_frame(list_3)
        assert isinstance(decoded, dict)
        pprint(decoded)
