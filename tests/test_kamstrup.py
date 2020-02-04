from pprint import pprint
from readams.meterdecode import kamstrup

list_1_three_phase = bytes.fromhex(
    "E6E700"
    "0F"
    "00000000"
    "0C07D0010106162100FF800001"
    "0219"
    "0A0E4B616D73747275705F5630303031"
    "09060101000005FF0A1035373036353637303030303030303030"
    "09060101600101FF0A12303030303030303030303030303030303030"
    "09060101010700FF0600000000"
    "09060101020700FF0600000000"
    "09060101030700FF0600000000"
    "09060101040700FF0600000000"
    "090601011F0700FF0600000000"
    "09060101330700FF0600000000"
    "09060101470700FF0600000000"
    "09060101200700FF120000"
    "09060101340700FF120000"
    "09060101480700FF120000")

list_2_single_phase = bytes.fromhex(
    "E6E700"
    "0F"
    "00000000"
    "0C07E1081003100005FF800000"
    "020F"
    "0A0E4B616D73747275705F5630303031"
    "09060101000005FF0A1035373036353637303030303030303030"
    "09060101600101FF0A12303030303030303030303030303030303030"
    "09060101010700FF0600000000"
    "090601011F0700FF0600000000"
    "09060101200700FF120000"
    "09060001010000FF"
    "090C07E1081003100005FF800000"
    "09060101010800FF0600000000")

list_2_three_phase = bytes.fromhex(
    "E6E700"
    "0F"
    "00000000"
    "0C07E1081003100005FF800000"
    "0223"
    "0A0E4B616D73747275705F5630303031"
    "09060101000005FF0A1035373036353637303030303030303030"
    "09060101600101FF0A12303030303030303030303030303030303030"
    "09060101010700FF0600000000"
    "09060101020700FF0600000000"
    "09060101030700FF0600000000"
    "09060101040700FF0600000000"
    "090601011F0700FF0600000000"
    "09060101330700FF0600000000"
    "09060101470700FF0600000000"
    "09060101200700FF120000"
    "09060101340700FF120000"
    "09060101480700FF120000"
    "09060001010000FF"
    "090C07E1081003100005FF800000"
    "09060101010800FF0600000000"
    "09060101020800FF0600000000"
    "09060101030800FF0600000000"
    "09060101040800FF0600000000")


def test_decode_list_1_three_phase():
    kamstrup_list_1_three_phase_parsed = kamstrup.LlcPdu.parse(list_1_three_phase)
    print(kamstrup_list_1_three_phase_parsed)


def test_decode_list_2_single_phase():
    kamstrup_list_2_single_phase_parsed = kamstrup.LlcPdu.parse(list_2_single_phase)
    print(kamstrup_list_2_single_phase_parsed)


def test_decode_list_2_three_phase():
    kamstrup_list_2_three_phase_parsed = kamstrup.LlcPdu.parse(list_2_three_phase)
    print(kamstrup_list_2_three_phase_parsed)


def test_decode_frame_list_1_three_phase():
    decoded = kamstrup.decode_frame(list_1_three_phase)
    pprint(decoded)


def test_decode_frame_list_2_three_phase():
    decoded = kamstrup.decode_frame(list_2_three_phase)
    pprint(decoded)


def test_decode_frame_list_2_single_phase():
    decoded = kamstrup.decode_frame(list_2_single_phase)
    pprint(decoded)
