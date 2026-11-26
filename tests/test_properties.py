"""Property based tests (Hypothesis) for readers and decoders."""

from __future__ import annotations

import re

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from han import aidon, dlde, hdlc
from han.autodecoder import AutoDecoder
from tests import frames

u32 = st.integers(min_value=0, max_value=2**32 - 1)
noise_without_flag = st.binary(max_size=40).map(lambda b: b.replace(b"\x7e", b""))


# A frame swallowed by a broken one is released at the first flag after the broken frame
# has passed its length field, so more frames must follow (as they do in a meter stream).
# 50 frames of 46 octets are more than the largest length field (2047).
_MORE_FRAMES = (
    frames.hdlc_frame(
        frames.data_notification(
            frames.aidon_list(
                frames.aidon_register(
                    "1.0.1.7.0.255", frames.double_long_unsigned(1), 0, 27
                )
            )
        )
    )
    * 50
)


@st.composite
def aidon_hdlc_frame(draw: st.DrawFn) -> bytes:
    registers = [
        frames.aidon_register(
            f"1.0.{code}.7.0.255", frames.double_long_unsigned(draw(u32)), 0, 27
        )
        for code in draw(
            st.lists(st.integers(1, 99), min_size=1, max_size=12, unique=True)
        )
    ]
    return frames.hdlc_frame(frames.data_notification(frames.aidon_list(*registers)))


@st.composite
def p1_readout(draw: st.DrawFn) -> bytes:
    values = draw(st.lists(st.integers(0, 99_999), min_size=1, max_size=5))
    return frames.p1_readout(
        "LGF5E360",
        [f"1-0:{i + 1}.7.0({v / 1000:06.3f}*kW)" for i, v in enumerate(values)],
    )


def split(data: bytes, cuts: list[int]) -> list[bytes]:
    points = sorted({c % (len(data) + 1) for c in cuts})
    return [data[a:b] for a, b in zip([0, *points], [*points, len(data)])]


def read_all(reader: hdlc.HdlcFrameReader | dlde.ModeDReader, chunks: list[bytes]):
    return [m for chunk in chunks for m in reader.read(chunk)]


@given(
    noise=noise_without_flag,
    stream_frames=st.lists(aidon_hdlc_frame(), min_size=1, max_size=4),
    cuts=st.lists(st.integers(min_value=0), max_size=20),
)
def test_hdlc_reader_is_independent_of_chunking(
    noise: bytes, stream_frames: list[bytes], cuts: list[int]
) -> None:
    # F16: a flag octet in the header (length, address, control, HCS) is xfail tested in test_hdlc.py
    assume(all(0x7E not in f[1:9] for f in stream_frames))
    stream = noise + b"".join(stream_frames)

    read = read_all(hdlc.HdlcFrameReader(use_octet_stuffing=False), split(stream, cuts))

    assert [f.as_bytes for f in read] == [f[1:-1] for f in stream_frames]
    assert all(f.is_valid for f in read)


@given(
    readouts=st.lists(p1_readout(), min_size=1, max_size=4),
    cuts=st.lists(st.integers(min_value=0), max_size=20),
)
def test_p1_reader_is_independent_of_chunking(
    readouts: list[bytes], cuts: list[int]
) -> None:
    stream = b"".join(readouts)

    read = read_all(dlde.ModeDReader(), split(stream, cuts))

    assert [r.as_bytes for r in read] == readouts
    assert all(r.is_valid for r in read)


@given(
    data=st.binary(max_size=600),
    cuts=st.lists(st.integers(min_value=0), max_size=10),
    stuffing=st.booleans(),
)
def test_hdlc_reader_never_raises_on_noise(
    data: bytes, cuts: list[int], stuffing: bool
) -> None:
    read_all(hdlc.HdlcFrameReader(use_octet_stuffing=stuffing), split(data, cuts))


p1_noise = st.lists(
    st.one_of(
        st.sampled_from(
            [b"/", b"!", b"\r\n", b"\n", b"LGF5E360", b"1-0:1.7.0(", b"*kW)"]
        ),
        st.binary(max_size=8),
    ),
    max_size=60,
).map(b"".join)


@given(data=p1_noise, cuts=st.lists(st.integers(min_value=0), max_size=10))
def test_p1_reader_never_raises_on_noise(data: bytes, cuts: list[int]) -> None:
    # F17: non-ASCII on a line starting with "/" (xfail tested in test_dlde.py)
    assume(not re.search(rb"/[^\n]*[\x80-\xff]", data))

    read_all(dlde.ModeDReader(), split(data, cuts))


@given(data=st.binary(max_size=600))
def test_autodecoder_never_raises_on_noise(data: bytes) -> None:
    # F18: ASCII with "(" can make the P1 parser loop forever (xfail tested in test_dlde.py)
    assume(not (data.isascii() and b"(" in data))
    decoded = AutoDecoder().decode_message_payload(data)

    assert decoded is None or isinstance(decoded, dict)


@given(frame=aidon_hdlc_frame(), length=st.integers(min_value=0))
def test_autodecoder_never_raises_on_truncated_payload(
    frame: bytes, length: int
) -> None:
    payload = frame[9:-3]  # information field: after flag, header and HCS
    truncated = payload[: length % (len(payload) + 1)]

    decoded = AutoDecoder().decode_message_payload(truncated)

    assert decoded is None or isinstance(decoded, dict)


@given(
    value=u32,
    scaler=st.integers(min_value=-3, max_value=3),
)
def test_aidon_register_scaling_roundtrip(value: int, scaler: int) -> None:
    decoded = aidon.decode_frame_content(
        frames.data_notification(
            frames.aidon_list(
                frames.aidon_register(
                    "1.0.1.7.0.255", frames.double_long_unsigned(value), scaler, 27
                )
            )
        )
    )

    assert decoded["active_power_import"] == pytest.approx(value * 10**scaler)


@given(
    noise=noise_without_flag,
    items=st.lists(
        st.tuples(aidon_hdlc_frame(), st.one_of(st.none(), st.integers(1, 200))),
        min_size=1,
        max_size=6,
    ),
    cuts=st.lists(st.integers(min_value=0), max_size=20),
)
def test_hdlc_reader_recovers_after_truncated_frames(
    noise: bytes, items: list[tuple[bytes, int | None]], cuts: list[int]
) -> None:
    # Each item is a complete frame, or (cut is not None) only a truncated prefix of it.
    # A flag octet in the header (length, address, control, HCS) still discards the
    # frame; that is an xfail test in test_hdlc.py.
    assume(all(0x7E not in f[1:9] for f, _ in items))
    stream = (
        noise
        + b"".join(f if c is None else f[: 1 + c % (len(f) - 2)] for f, c in items)
        + _MORE_FRAMES
    )
    expected = [f[1:-1] for f, c in items if c is None]
    assume(expected)

    read = read_all(hdlc.HdlcFrameReader(use_octet_stuffing=False), split(stream, cuts))

    valid = [f.as_bytes for f in read if f.is_good_ffc and f.is_expected_length]
    assert valid[: len(expected)] == expected
