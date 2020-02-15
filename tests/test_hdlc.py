from meterdecode import hdlc

_frame_list_1 = bytes.fromhex(
    "7e"
    "a027010201105a87e6e7000f40000000090c07e4020f06010830ff80000002010600001fc7cec3"
    "7e")

_frame_list_2 = bytes.fromhex(
    "7e"
    "a079010201108093e6e7000f40000000090c07e4020f06010832ff800000020d09074b464d5f30303109103639373036333134303236313434373609084d413330344833450600001fbf0600000000060000000006000001c406000089540600007fcd06000014b8060000085406000000000600000893384f"
    "7e")

_frame_with_escape_character = bytes.fromhex(
    "7e"
    "a079010201108093e6e7000f40000000090c07e4020f0601001eff800000020d09074b464d5f30303109103639373036333134303236313434373609084d413330344833450600001d150600000000060000000006000001bd0600008352060000801d06000008f706000008520600000000060000089a"
    "7d43"
    "7e")

_frame_with_control_caracter_in_content = bytes.fromhex(
    "7e"
    "a027010201105a87e6e7000f40000000090c07e4020f06011922ff800000020106000015"
    "7e"
    "ea5e"
    "7e")


def test_frame_with_escape_character():
    frame_reader = hdlc.HdlcOctetStuffedFrameReader()
    frames = frame_reader.read(_frame_with_escape_character)

    assert frames is not None
    assert len(frames) == 1
    assert frames[0].is_good


def test_frame_with_control_caracter_in_content():
    frame_reader = hdlc.HdlcOctetStuffedFrameReader()
    frames = frame_reader.read(_frame_with_control_caracter_in_content)

    assert frames is not None
    assert len(frames) == 1
    assert frames[0].is_good
