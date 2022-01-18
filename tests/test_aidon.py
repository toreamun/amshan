"""Aidon tests."""
# pylint: disable = no-self-use
from pprint import pprint

import construct

from amshan import aidon

no_list_1 = bytes.fromhex(
    "e6e700" "0f" "40000000" "00" "0101" "020309060100010700ff060000011802020f00161b"
)

no_list_2 = bytes.fromhex(
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
    "020309060100480700ff12090402020fff1623"
)

no_list_3 = bytes.fromhex(
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
    "02020f011620"
)

# From https://www.tekniskaverken.se/siteassets/tekniska-verken/elnat/aidonfd-rj12-han-interface-sv-v15d.pdf
se_list = bytes.fromhex(
    (
        "e6e700"
        "0f 40000000 00"
        "011b"
        "0202 0906 0000010000ff 090c 07e30c1001073b28ff8000ff"
        "0203 0906 0100010700ff 06 00000462 0202 0f00 161b"
        "0203 0906 0100020700ff 06 00000000 0202 0f00 161b"
        "0203 0906 0100030700ff 06 000005e3 0202 0f00 161d"
        "0203 0906 0100040700ff 06 00000000 0202 0f00 161d"
        "0203 0906 01001f0700ff 10 00000202 0fff 1621"
        "0203 0906 0100330700ff 10 004b0202 0fff 1621"
        "0203 0906 0100470700ff 10 00000202 0fff 1621"
        "0203 0906 0100200700ff 12 09030202 0fff 1623"
        "0203 0906 0100340700ff 12 09c30202 0fff 1623"
        "0203 0906 0100480700ff 12 09040202 0fff 1623"
        "0203 0906 0100150700ff 06 00000000 0202 0f00 161b"
        "0203 0906 0100160700ff 06 00000000 0202 0f00 161b"
        "0203 0906 0100170700ff 06 00000000 0202 0f00 161d"
        "0203 0906 0100180700ff 06 00000000 0202 0f00 161d"
        "0203 0906 0100290700ff 06 00000462 0202 0f00 161b"
        "0203 0906 01002a0700ff 06 00000000 0202 0f00 161b"
        "0203 0906 01002b0700ff 06 000005e2 0202 0f00 161d"
        "0203 0906 01002c0700ff 06 00000000 0202 0f00 161d"
        "0203 0906 01003d0700ff 06 00000000 0202 0f00 161b"
        "0203 0906 01003e0700ff 06 00000000 0202 0f00 161b"
        "0203 0906 01003f0700ff 06 00000000 0202 0f00 161d"
        "0203 0906 0100400700ff 06 00000000 0202 0f00 161d"
        "0203 0906 0100010800ff 06 00995986 0202 0f00 161e"
        "0203 0906 0100020800ff 06 00000008 0202 0f00 161e"
        "0203 0906 0100030800ff 06 0064ed4b 0202 0f00 1620"
        "0203 0906 0100040800ff 06 00000005 0202 0f00 1620"
    ).replace(" ", "")
)


class TestParseAidon:
    """Test parse Aidon frames."""

    def test_parse_se_list(self):
        """Parse swedish list number 1."""
        parsed = aidon.LlcPdu.parse(se_list)
        assert isinstance(parsed, construct.Container)
        print(parsed)

    def test_parse_no_list_1(self):
        """Parse list number 1."""
        parsed = aidon.LlcPdu.parse(no_list_1)
        assert isinstance(parsed, construct.Container)
        print(parsed)

    def test_parse_no_list_2(self):
        """Parse list number 2."""
        parsed = aidon.LlcPdu.parse(no_list_2)
        assert isinstance(parsed, construct.Container)
        print(parsed)

    def test_parse_no_list_3(self):
        """Parse list number 2."""
        parsed = aidon.LlcPdu.parse(no_list_3)
        assert isinstance(parsed, construct.Container)
        print(parsed)


class TestDecodeAidon:
    """Test decode Aidon frames."""

    def test_decode_frame_no_list_1(self):
        """Decode list number 1."""
        decoded = aidon.decode_frame_content(no_list_1)
        assert isinstance(decoded, dict)
        pprint(decoded)

    def test_decode_frame_no_list_2(self):
        """Decode list number 2."""
        decoded = aidon.decode_frame_content(no_list_2)
        assert isinstance(decoded, dict)
        pprint(decoded)

    def test_decode_frame_no_list_3(self):
        """Decode list number 3."""
        decoded = aidon.decode_frame_content(no_list_3)
        assert isinstance(decoded, dict)
        pprint(decoded)
