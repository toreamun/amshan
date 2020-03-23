import asyncio
import logging
from typing import Optional, Callable, Tuple

import serial_asyncio

from smartmeterdecode import hdlc


class SmartMeterProtocol(asyncio.Protocol):
    def __init__(
        self,
        queue: asyncio.Queue,
        on_connection_lost: asyncio.Future = None,
        frame_reader=hdlc.HdlcFrameReader(
            use_octet_stuffing=False, use_abort_sequence=True
        ),
    ) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__)
        self._transport = None
        self._queue = queue
        self._on_con_lost_future = on_connection_lost
        self._frame_reader = frame_reader

    @property
    def on_connection_lost(self) -> Optional[asyncio.Future]:
        return self._on_con_lost_future

    def _get_transport_info(self):
        info = None

        if hasattr(self._transport, "serial"):
            info = str(self._transport.serial)
        else:
            peer_name = self._transport.get_extra_info("peername")
            if peer_name:
                host, port = peer_name
                info = "host {} on port {}".format(host, port)

        if not info:
            info = str(self._transport)

        return info

    def connection_made(self, transport):
        """Called when a connection is made.

        The argument is the transport representing the connection.
        To receive data, wait for data_received() calls.
        When the connection is closed, connection_lost() is called.
        """
        self._transport = transport
        self._logger.debug("Connected to %s", self._get_transport_info())

    def connection_lost(self, exc):
        """Called when the connection is lost or closed.

        The argument is an exception object or None (the latter
        meaning a regular EOF is received or the connection was
        aborted or closed).
        """
        if exc:
            self._logger.exception(
                "Connection to %s lost: %s", self._get_transport_info(), exc
            )
        else:
            self._logger.debug(
                "Connection to %s aborted or closed.", self._get_transport_info()
            )

        self._transport.close()

        if self._on_con_lost_future:
            self._on_con_lost_future.set_result(True)

        super().connection_lost(exc)

    def data_received(self, data):
        """Called when some data is received.

        The argument is a bytes object.
        """
        frames = self._frame_reader.read(data)
        for frame in frames:
            self._queue.put_nowait(frame)


class SmartMeterConnection:
    """
    Maintain connection to smart meter data feed.
    """

    def __init__(
        self,
        connection_factory: Callable[[], Tuple[asyncio.Transport, SmartMeterProtocol]],
    ) -> None:
        """
        Initialize class.
        :param connection_factory: A factory function that returns a Transport and SmartMeterProtocol tuple.
        """

        self._connection_factory: Callable[
            [], (asyncio.Transport, SmartMeterProtocol)
        ] = connection_factory
        self._connection: (asyncio.Transport, SmartMeterProtocol) = None
        self._is_closing = False
        self._connection_count = 0

    async def connect(self):
        """
        Connect to meter using connection factory, and keep reconnecting if connection is lost.
        The connection is not reconnected on connection loss if close() was called on this instance.
        """
        while not self._is_closing:
            self._connection_count = self._connection_count + 1
            self._connection = await self._connection_factory()
            _, protocol = self._connection
            await protocol.on_connection_lost
            self._connection = None

        self._is_closing = False

    def close(self):
        """Close current connection, if any, and stop reconnecting."""
        if self._connection:
            self._is_closing = True
            transport, _ = self._connection
            transport.close()


async def create_meter_serial_connection(
    loop, queue: asyncio.Queue, *args, **kwargs
) -> (serial_asyncio.SerialTransport, SmartMeterProtocol):
    """
    Create serial connection using :class:`SmartMeterProtocol`

    :param loop: The event handler
    :param queue: Queue for received frames
    :param args: Passed to the :class:`serial.Serial` init function
    :param kwargs: Passed to the :class:`serial.Serial` init function
    :return: Tuple of transport and protocol
    """
    on_connection_lost = loop.create_future()
    return await serial_asyncio.create_serial_connection(
        loop, lambda: SmartMeterProtocol(queue, on_connection_lost), *args, **kwargs
    )


async def create_meter_tcp_connection(
    loop, queue: asyncio.Queue, *args, **kwargs
) -> (asyncio.Transport, SmartMeterProtocol):
    """
    Create TCP connection using :class:`SmartMeterProtocol`

    :param loop: The event handler
    :param queue: Queue for received frames
    :param args: Passed to the :class:`loop.create_connection`
    :param kwargs: Passed to the :class:`loop.create_connection`
    :return: Tuple of transport and protocol
    """
    on_connection_lost = loop.create_future()
    return await loop.create_connection(
        lambda: SmartMeterProtocol(queue, on_connection_lost), *args, **kwargs
    )
