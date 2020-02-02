from pprint import pprint
from readams.meterdecode import kaifa
import logging

logging.basicConfig(level=logging.DEBUG)


class TestDecodeKaifa:
    kaifa_list_1 = bytes.fromhex(
        'e6e700'
        '0f'
        '40000000'
        '090c07e3020401173416ff800000'
        '0201'
        '06000016dc'
    )

    kaifa_list_2 = bytes.fromhex(
        'e6e7000f40000000090c07e40119060d091eff800000020d09074b464d5f30303109103639373036333134303236313434373609084d4133303448334506000026110600000000060000000006000001b306000084150600006dc7060000470206000008780600000000060000088c')

    kaifa_list_3 = bytes.fromhex(
        'e6e7000f40000000090c07e40119060e000aff800000021209074b464d5f30303109103639373036333134303236313434373609084d41333034483345060000132806000000000600000000060000017906000038eb0600003d1b060000253506000008910600000000060000089d090c07e40119060e000aff8000000604be76e8060000000006000d922d060030feb4')

    def test_decode_list_1(self):
        msg = kaifa.LlcPdu.parse(self.kaifa_list_1)
        print(msg)

    def test_decode_list_2(self):
        msg = kaifa.LlcPdu.parse(self.kaifa_list_2)
        print(msg)

    def test_decode_list_3(self):
        msg = kaifa.LlcPdu.parse(self.kaifa_list_3)
        print(msg)

    def test_decode_frame_list_1(self):
        decoded = kaifa.decode_frame(self.kaifa_list_1)
        pprint(decoded)

    def test_decode_frame_list_2(self):
        decoded = kaifa.decode_frame(self.kaifa_list_2)
        pprint(decoded)

    def test_decode_frame_list_3(self):
        decoded = kaifa.decode_frame(self.kaifa_list_3)
        pprint(decoded)

# print(kaifaMsg1)
#print(kaifaMsg2)
# print(kaifaMsg3)

# kaifa_msg_1_dic = kaifa_message_to_dictionary(kaifaMsg1)
# print(json.dumps(kaifa_msg_1_dic, indent=3))

# kaifa_msg_2_dic = kaifa_message_to_dictionary(kaifaMsg2)
# print(json.dumps(kaifa_msg_2_dic, indent=3))

# kaifa_msg_3_dic = kaifa_message_to_dictionary(kaifaMsg3)
# print(json.dumps(kaifa_msg_3_dic, indent=3))
