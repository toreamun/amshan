"""Build synthetic meter frames for tests.

The frames are built from scratch with made-up values, so tests do not depend on
captured consumption data.
"""

from __future__ import annotations

from han.fastframecheck import FastFrameCheckSequence16

FLAG = b"\x7e"
LLC = bytes.fromhex("e6e700")


def checksum(data: bytes) -> bytes:
    """Return HDLC check sequence (HCS/FCS) as transmitted (little endian)."""
    return FastFrameCheckSequence16.compute_checksum(data, 0, len(data)).to_bytes(
        2, "little"
    )


def hdlc_frame(
    information: bytes,
    destination: bytes = b"\x41",
    source: bytes = b"\x08\x83",
    control: int = 0x13,
    flags: bool = True,
) -> bytes:
    """Build a HDLC frame (type 3 format) with correct HCS and FCS.

    A frame without information field has only FCS, no HCS.
    """
    address_control = destination + source + bytes([control])
    hcs_length = 2 if information else 0
    length = 2 + len(address_control) + hcs_length + len(information) + 2
    assert length < 0x800, "frame length must fit in 11 bits"
    frame_format = (0xA000 | length).to_bytes(2, "big")
    header = frame_format + address_control
    if information:
        header += checksum(header)
    body = header + information
    body += checksum(body)
    return FLAG + body + FLAG if flags else body


def data_notification(body: bytes, date_time: bytes = b"\x00") -> bytes:
    """Build LLC + DLMS data-notification APDU with the given notification body."""
    return LLC + b"\x0f" + b"\x40\x00\x00\x00" + date_time + body


def obis(code: str) -> bytes:
    """Encode an OBIS code 'a.b.c.d.e.f' as COSEM octet-string."""
    return b"\x09\x06" + bytes(int(x) for x in code.split("."))


def visible_string(text: str) -> bytes:
    """Encode a COSEM visible-string."""
    data = text.encode("ascii")
    return b"\x0a" + bytes([len(data)]) + data


def double_long_unsigned(value: int) -> bytes:
    """Encode a COSEM double-long-unsigned (type 6)."""
    return b"\x06" + value.to_bytes(4, "big")


def double_long(value: int) -> bytes:
    """Encode a COSEM double-long (type 5, signed 32 bit)."""
    return b"\x05" + value.to_bytes(4, "big", signed=True)


def long_unsigned(value: int) -> bytes:
    """Encode a COSEM long-unsigned (type 18)."""
    return b"\x12" + value.to_bytes(2, "big")


def scaler_unit(scaler: int, unit: int) -> bytes:
    """Encode a COSEM scaler-unit structure."""
    return (
        b"\x02\x02\x0f"
        + scaler.to_bytes(1, "big", signed=True)
        + b"\x16"
        + bytes([unit])
    )


def aidon_register(code: str, value: bytes, scaler: int, unit: int) -> bytes:
    """Encode an Aidon style register element (obis, value, scaler-unit)."""
    return b"\x02\x03" + obis(code) + value + scaler_unit(scaler, unit)


def aidon_list(*elements: bytes) -> bytes:
    """Encode an Aidon style array of elements."""
    return b"\x01" + bytes([len(elements)]) + b"".join(elements)


def p1_readout(ident: str, lines: list[str]) -> bytes:
    """Build a P1 (IEC 62056-21 mode D) readout with correct CRC16."""
    body = f"/{ident}\r\n\r\n" + "".join(f"{line}\r\n" for line in lines) + "!"
    crc = crc16_arc(body.encode("ascii"))
    return (body + f"{crc:04X}\r\n").encode("ascii")


def crc16_arc(data: bytes) -> int:
    """CRC-16/ARC used by P1 (IEC 62056-21 mode D) readouts."""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc


def aidon_frame_with_last_octet(value: int) -> bytes:
    """A valid Aidon HDLC frame whose last octet before the closing flag is ``value``.

    The last octet is the high byte of the frame check sequence. Used to build frames
    ending with 0x7D (HDLC control escape).
    """
    for n in range(100_000):
        frame = hdlc_frame(
            data_notification(
                aidon_list(
                    aidon_register("1.0.1.7.0.255", double_long_unsigned(n), 0, 27)
                )
            )
        )
        if frame[-2] == value:
            return frame
    raise AssertionError("no such frame found")
