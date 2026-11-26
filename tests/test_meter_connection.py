"""Tests for han.meter_connection."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import pytest

from han import meter_connection
from han.dlde import ModeDReader
from han.hdlc import HdlcFrameReader
from han.meter_connection import (
    ConnectionManager,
    ExponentialBackOff,
    SmartMeterMessagePayloadProtocol,
    SmartMeterMessageProtocol,
)
from tests import frames

INFORMATION = frames.data_notification(
    frames.aidon_list(
        frames.aidon_register("1.0.1.7.0.255", frames.double_long_unsigned(1000), 0, 27)
    )
)
FRAME = frames.hdlc_frame(INFORMATION)


class FakeTransport:
    """Minimal transport used by the protocols."""

    def __init__(self, peername: Any = ("10.0.0.1", 3001)) -> None:
        self.peername = peername
        self.closed = 0
        self.fail_on_close = False

    def get_extra_info(self, name: str, default: Any = None) -> Any:
        return self.peername if name == "peername" else default

    def close(self) -> None:
        self.closed += 1
        if self.fail_on_close:
            raise OSError("close failed")


class FakeSerialTransport(FakeTransport):
    """Transport with a serial attribute, like serial_asyncio.SerialTransport."""

    serial = "Serial<port='/dev/ttyUSB0'>"


def hdlc_readers() -> list[Any]:
    return [HdlcFrameReader(use_octet_stuffing=False)]


class TestExponentialBackOff:
    """ExponentialBackOff."""

    def test_doubles_up_to_max_and_resets(self) -> None:
        back_off = ExponentialBackOff()
        assert back_off.current_delay_sec == 0

        delays = []
        for _ in range(8):
            back_off.failure()
            delays.append(back_off.current_delay_sec)
        assert delays == [1, 2, 4, 8, 16, 32, 60, 60]

        back_off.reset()
        assert back_off.current_delay_sec == 0


class TestSmartMeterMessageProtocol:
    """SmartMeterMessageProtocol and the common base protocol."""

    async def test_frames_in_chunks_are_queued(self) -> None:
        queue: asyncio.Queue[Any] = asyncio.Queue()
        protocol = SmartMeterMessageProtocol(queue, hdlc_readers())
        protocol.connection_made(FakeTransport())  # type: ignore[arg-type]

        data = FRAME + FRAME
        for start in range(0, len(data), 7):
            protocol.data_received(data[start : start + 7])

        assert queue.qsize() == 2
        message = queue.get_nowait()
        assert message.is_valid
        assert message.payload == INFORMATION

    async def test_reader_is_selected_from_candidates(self) -> None:
        queue: asyncio.Queue[Any] = asyncio.Queue()
        readout = frames.p1_readout("ABC5TEST", ["1-0:1.7.0(01.000*kW)"])
        protocol = SmartMeterMessageProtocol(
            queue, [HdlcFrameReader(use_octet_stuffing=False), ModeDReader()]
        )
        protocol.connection_made(FakeTransport())  # type: ignore[arg-type]

        protocol.data_received(readout)
        protocol.data_received(readout)

        assert queue.qsize() == 2
        assert all(queue.get_nowait().is_valid for _ in range(2))

    async def test_nothing_queued_before_a_valid_message(self) -> None:
        queue: asyncio.Queue[Any] = asyncio.Queue()
        protocol = SmartMeterMessageProtocol(queue, hdlc_readers())
        protocol.connection_made(FakeTransport())  # type: ignore[arg-type]

        broken = bytearray(FRAME)
        broken[-3] ^= 0xFF  # corrupt FCS
        protocol.data_received(bytes(broken))

        assert queue.empty()

    async def test_invalid_message_after_selection_is_queued(self) -> None:
        queue: asyncio.Queue[Any] = asyncio.Queue()
        protocol = SmartMeterMessageProtocol(queue, hdlc_readers())
        protocol.connection_made(FakeTransport())  # type: ignore[arg-type]
        protocol.data_received(FRAME)

        broken = bytearray(FRAME)
        broken[-3] ^= 0xFF
        protocol.data_received(bytes(broken))

        assert queue.qsize() == 2
        queue.get_nowait()
        assert not queue.get_nowait().is_valid

    async def test_connection_lost_closes_transport_and_sets_done(self) -> None:
        protocol = SmartMeterMessageProtocol(asyncio.Queue(), hdlc_readers())
        transport = FakeTransport()
        protocol.connection_made(transport)  # type: ignore[arg-type]

        protocol.connection_lost(ConnectionResetError("reset"))

        assert transport.closed == 1
        await asyncio.wait_for(protocol.done, 1)

    async def test_connection_lost_survives_failing_close(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        protocol = SmartMeterMessageProtocol(asyncio.Queue(), hdlc_readers())
        transport = FakeTransport()
        transport.fail_on_close = True
        protocol.connection_made(transport)  # type: ignore[arg-type]

        with caplog.at_level(logging.WARNING):
            protocol.connection_lost(None)

        assert "Error when closing transport" in caplog.text
        await asyncio.wait_for(protocol.done, 1)

    @pytest.mark.parametrize(
        ("transport", "expected"),
        [
            (FakeTransport(("10.0.0.1", 3001)), "host 10.0.0.1 and port 3001"),
            (FakeSerialTransport(), "Serial<port='/dev/ttyUSB0'>"),
            (FakeTransport(None), "FakeTransport"),
        ],
    )
    async def test_transport_info_is_logged(
        self, transport: FakeTransport, expected: str, caplog: pytest.LogCaptureFixture
    ) -> None:
        protocol = SmartMeterMessageProtocol(asyncio.Queue(), hdlc_readers())

        with caplog.at_level(logging.INFO):
            protocol.connection_made(transport)  # type: ignore[arg-type]

        assert expected in caplog.text

    async def test_eof_closes_transport(self) -> None:
        protocol = SmartMeterMessageProtocol(asyncio.Queue(), hdlc_readers())
        assert protocol.eof_received() is False

    async def test_instances_get_increasing_ids(self) -> None:
        first = SmartMeterMessageProtocol(asyncio.Queue(), hdlc_readers())
        second = SmartMeterMessageProtocol(asyncio.Queue(), hdlc_readers())
        assert second.instance_id == first.instance_id + 1


class TestSmartMeterMessagePayloadProtocol:
    """SmartMeterMessagePayloadProtocol."""

    async def test_payload_of_valid_message_is_queued(self) -> None:
        queue: asyncio.Queue[bytes] = asyncio.Queue()
        protocol = SmartMeterMessagePayloadProtocol(queue, hdlc_readers())
        protocol.connection_made(FakeTransport())  # type: ignore[arg-type]

        protocol.data_received(FRAME)

        assert queue.get_nowait() == INFORMATION

    async def test_empty_and_invalid_messages_are_not_queued(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        queue: asyncio.Queue[bytes] = asyncio.Queue()
        protocol = SmartMeterMessagePayloadProtocol(queue, hdlc_readers())
        protocol.connection_made(FakeTransport())  # type: ignore[arg-type]
        protocol.data_received(FRAME)
        queue.get_nowait()

        broken = bytearray(FRAME)
        broken[-3] ^= 0xFF
        with caplog.at_level(logging.DEBUG):
            protocol.data_received(frames.hdlc_frame(b""))
            protocol.data_received(bytes(broken))

        assert queue.empty()
        assert "Got empty message." in caplog.text
        assert "Got invalid message" in caplog.text


class FakeConnections:
    """Connection factory returning protocols with fake transports."""

    def __init__(self, failures: int = 0) -> None:
        self.failures = failures
        self.calls = 0
        self.protocols: list[SmartMeterMessageProtocol] = []
        self.transports: list[FakeTransport] = []
        self.connected = asyncio.Event()

    async def factory(self) -> Any:
        self.calls += 1
        if self.calls <= self.failures:
            raise ConnectionRefusedError("refused")
        transport = FakeTransport()
        protocol = SmartMeterMessageProtocol(asyncio.Queue(), hdlc_readers())
        protocol.connection_made(transport)  # type: ignore[arg-type]
        self.transports.append(transport)
        self.protocols.append(protocol)
        self.connected.set()
        return transport, protocol

    async def wait_connected(self) -> SmartMeterMessageProtocol:
        await asyncio.wait_for(self.connected.wait(), 2)
        self.connected.clear()
        return self.protocols[-1]


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record back-off sleeps instead of waiting."""
    recorded: list[float] = []
    real_sleep = asyncio.sleep

    async def fake_sleep(delay: float) -> None:
        recorded.append(delay)
        await real_sleep(0)

    monkeypatch.setattr(meter_connection, "sleep", fake_sleep)
    return recorded


class TestConnectionManager:
    """ConnectionManager."""

    def test_factory_must_be_coroutine_function(self) -> None:
        with pytest.raises(ValueError, match="awaitable"):
            ConnectionManager(lambda: None)  # type: ignore[arg-type,return-value]

    async def test_close_stops_loop_and_closes_transport(
        self, sleeps: list[float]
    ) -> None:
        connections = FakeConnections()
        manager = ConnectionManager(connections.factory)
        loop_task = asyncio.create_task(manager.connect_loop())

        await connections.wait_connected()
        manager.close()
        await asyncio.wait_for(loop_task, 2)

        assert connections.calls == 1
        assert connections.transports[0].closed == 1
        assert sleeps == []

    async def test_reconnects_when_connection_is_lost(
        self, sleeps: list[float]
    ) -> None:
        connections = FakeConnections()
        manager = ConnectionManager(connections.factory)
        loop_task = asyncio.create_task(manager.connect_loop())

        protocol = await connections.wait_connected()
        protocol.connection_lost(ConnectionResetError())
        await connections.wait_connected()

        manager.close()
        await asyncio.wait_for(loop_task, 2)
        assert connections.calls == 2
        assert sleeps == []

    async def test_backs_off_exponentially_after_connect_errors(
        self, sleeps: list[float]
    ) -> None:
        connections = FakeConnections(failures=3)
        manager = ConnectionManager(connections.factory)
        loop_task = asyncio.create_task(manager.connect_loop())

        await connections.wait_connected()
        manager.close()
        await asyncio.wait_for(loop_task, 2)

        assert connections.calls == 4
        assert sleeps == [1, 2, 4]
        assert manager.back_off_connect_error.current_delay_sec == 0

    async def test_sleeps_when_connection_is_lost_twice_quickly(
        self, sleeps: list[float]
    ) -> None:
        connections = FakeConnections()
        manager = ConnectionManager(connections.factory)
        loop_task = asyncio.create_task(manager.connect_loop())

        (await connections.wait_connected()).connection_lost(None)
        (await connections.wait_connected()).connection_lost(None)
        await connections.wait_connected()

        manager.close()
        await asyncio.wait_for(loop_task, 2)
        assert sleeps == [manager.connection_lost_back_off_sleep_sec]

    async def test_close_while_waiting_for_back_off(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        connections = FakeConnections(failures=100)
        manager = ConnectionManager(connections.factory)
        sleeping = asyncio.Event()

        async def slow_sleep(_delay: float) -> None:
            sleeping.set()
            await asyncio.sleep(3600)

        monkeypatch.setattr(meter_connection, "sleep", slow_sleep)
        loop_task = asyncio.create_task(manager.connect_loop())

        await asyncio.wait_for(sleeping.wait(), 2)
        manager.close()
        await asyncio.wait_for(loop_task, 2)

        assert connections.calls == 1

    async def test_loop_can_be_started_again_after_close(
        self, sleeps: list[float]
    ) -> None:
        connections = FakeConnections()
        manager = ConnectionManager(connections.factory)

        for _ in range(2):
            loop_task = asyncio.create_task(manager.connect_loop())
            await connections.wait_connected()
            manager.close()
            await asyncio.wait_for(loop_task, 2)

        assert connections.calls == 2


def pending_try_connect_tasks() -> list[asyncio.Task]:
    return [
        t
        for t in asyncio.all_tasks()
        if not t.done() and t.get_coro().__qualname__.endswith("._try_connect")
    ]


@pytest.mark.xfail(
    reason="F13: ConnectionManager leaves its connect task running after close()",
    strict=True,
    raises=AssertionError,
)
@pytest.mark.parametrize("phase", ["connecting", "back-off"])
async def test_connection_manager_close_stops_connect_task(phase: str) -> None:
    calls = 0
    never = asyncio.Event()

    async def factory() -> None:
        nonlocal calls
        calls += 1
        if phase == "back-off" and calls == 1:
            raise ConnectionRefusedError
        await never.wait()  # connection attempt in progress

    manager = meter_connection.ConnectionManager(factory)  # type: ignore[arg-type]
    loop_task = asyncio.create_task(manager.connect_loop())
    for _ in range(100):
        await asyncio.sleep(0)
        if calls == 1 and pending_try_connect_tasks():
            break
    tasks = pending_try_connect_tasks()
    assert len(tasks) == 1, "test setup: expected one connect attempt in progress"

    manager.close()
    await asyncio.wait_for(loop_task, 2)
    await asyncio.sleep(0)

    try:
        assert tasks[0].done()
    finally:
        tasks[0].cancel()
        await asyncio.gather(tasks[0], return_exceptions=True)
