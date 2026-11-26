"""Tests for the TCP and serial connection factories."""

from __future__ import annotations

import asyncio
import socket
from collections.abc import AsyncIterator
from typing import Any

import pytest

from han import serial_connection_factory, tcp_connection_factory
from han.meter_connection import (
    SmartMeterMessagePayloadProtocol,
    SmartMeterMessageProtocol,
)
from tests import frames

INFORMATION = frames.data_notification(
    frames.aidon_list(
        frames.aidon_register("1.0.1.7.0.255", frames.double_long_unsigned(500), 0, 27)
    )
)
FRAME = frames.hdlc_frame(INFORMATION)
READOUT = frames.p1_readout("ABC5TEST", ["1-0:1.7.0(00.500*kW)"])


@pytest.fixture
async def meter_server() -> AsyncIterator[tuple[str, int, list[bytes]]]:
    """Local TCP server that sends the queued data to each client.

    The connection is kept open until the client closes it.
    """
    to_send: list[bytes] = []
    handlers: list[asyncio.Task[None]] = []

    async def handle(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        handlers.append(asyncio.current_task())  # type: ignore[arg-type]
        try:
            for data in to_send:
                writer.write(data)
            await writer.drain()
            await reader.read()  # wait until the client closes
        finally:
            writer.close()
            await writer.wait_closed()

    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    host, port = server.sockets[0].getsockname()[:2]
    async with server:
        yield host, port, to_send
        await asyncio.wait_for(asyncio.gather(*handlers), 2)


async def _get(queue: asyncio.Queue[Any]) -> Any:
    return await asyncio.wait_for(queue.get(), 2)


@pytest.mark.parametrize("data", [FRAME, READOUT], ids=["hdlc", "p1"])
async def test_tcp_message_connection_with_default_readers(
    meter_server: tuple[str, int, list[bytes]], data: bytes
) -> None:
    host, port, to_send = meter_server
    to_send.append(data)
    queue: asyncio.Queue[Any] = asyncio.Queue()

    transport, protocol = await tcp_connection_factory.create_tcp_message_connection(
        queue, None, None, host, port
    )
    try:
        assert isinstance(protocol, SmartMeterMessageProtocol)
        message = await _get(queue)
        assert message.is_valid
        assert message.as_bytes.strip(b"~") in data
    finally:
        transport.close()


async def test_tcp_payload_connection(
    meter_server: tuple[str, int, list[bytes]],
) -> None:
    host, port, to_send = meter_server
    to_send.append(FRAME)
    queue: asyncio.Queue[bytes] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    (
        transport,
        protocol,
    ) = await tcp_connection_factory.create_tcp_message_payload_connection(
        queue, loop, None, host, port
    )
    try:
        assert isinstance(protocol, SmartMeterMessagePayloadProtocol)
        assert await _get(queue) == INFORMATION
    finally:
        transport.close()


async def test_tcp_connection_refused() -> None:
    # Keep the port bound but not listening, so no other process can take it.
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

        with pytest.raises(OSError):
            await tcp_connection_factory.create_tcp_message_connection(
                asyncio.Queue(), None, None, "127.0.0.1", port
            )


@pytest.mark.parametrize(
    ("factory", "protocol_type", "expected"),
    [
        (
            serial_connection_factory.create_serial_message_connection,
            SmartMeterMessageProtocol,
            None,
        ),
        (
            serial_connection_factory.create_serial_message_payload_connection,
            SmartMeterMessagePayloadProtocol,
            INFORMATION,
        ),
    ],
    ids=["message", "payload"],
)
async def test_serial_connection_over_socket_url(
    meter_server: tuple[str, int, list[bytes]],
    factory: Any,
    protocol_type: type,
    expected: bytes | None,
) -> None:
    """Serial factories pass url and settings on to the serial transport."""
    host, port, to_send = meter_server
    to_send.append(FRAME)
    queue: asyncio.Queue[Any] = asyncio.Queue()

    transport, protocol = await factory(
        queue, None, None, url=f"socket://{host}:{port}", baudrate=2400
    )
    try:
        assert isinstance(protocol, protocol_type)
        assert transport.serial.baudrate == 2400
        received = await _get(queue)
        if expected is None:
            assert received.is_valid
        else:
            assert received == expected
    finally:
        transport.close()


async def test_serial_connection_uses_given_readers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Explicit readers and loop are passed to the protocol and transport."""
    captured: dict[str, Any] = {}

    async def fake_create(loop: Any, factory: Any, *args: Any, **kwargs: Any) -> Any:
        captured.update(loop=loop, protocol=factory(), args=args, kwargs=kwargs)
        return "transport", captured["protocol"]

    monkeypatch.setattr(
        serial_connection_factory.serial_asyncio,
        "create_serial_connection",
        fake_create,
    )
    readers = [object()]
    loop = asyncio.get_running_loop()

    await serial_connection_factory.create_serial_message_connection(
        asyncio.Queue(),
        loop,
        readers,
        "/dev/ttyUSB0",
        baudrate=2400,  # type: ignore[list-item]
    )

    assert captured["loop"] is loop
    assert captured["protocol"]._reader_candidates == readers
    assert captured["args"] == ("/dev/ttyUSB0",)
    assert captured["kwargs"] == {"baudrate": 2400}


# A valid frame where the last FCS octet is 0x7D (HDLC control escape).
FRAME_FCS_7D = frames.aidon_frame_with_last_octet(0x7D)


@pytest.mark.xfail(
    reason="the factories discard a valid frame ending with 0x7D", strict=True
)
@pytest.mark.parametrize("transport_kind", ["tcp", "serial"])
async def test_factory_keeps_valid_frame_ending_with_control_escape(
    meter_server: tuple[str, int, list[bytes]], transport_kind: str
) -> None:
    host, port, to_send = meter_server
    to_send.extend([FRAME_FCS_7D, FRAME])
    queue: asyncio.Queue[Any] = asyncio.Queue()

    if transport_kind == "tcp":
        transport, _ = await tcp_connection_factory.create_tcp_message_connection(
            queue, None, None, host, port
        )
    else:
        transport, _ = await serial_connection_factory.create_serial_message_connection(
            queue, None, None, url=f"socket://{host}:{port}", baudrate=2400
        )
    try:
        first = await _get(queue)
        assert first.is_valid
        assert first.as_bytes == FRAME_FCS_7D[1:-1]
    finally:
        transport.close()
