import asyncio
import logging
from abc import ABCMeta, abstractmethod
from asyncio import FIRST_COMPLETED
from typing import Callable, Optional, Tuple

import serial_asyncio

from smartmeterdecode import hdlc

_LOGGER = logging.getLogger(__name__)


class SmartMeterProtocol(asyncio.ReadTransport):

    connections = 0

    def __init__(self, queue: asyncio.Queue, frame_reader=None) -> None:
        super().__init__()
        self.queue: asyncio.Queue = queue
        self._frame_reader = (
            frame_reader
            if frame_reader
            else hdlc.HdlcFrameReader(use_octet_stuffing=False, use_abort_sequence=True)
        )
        self.done: asyncio.Future = asyncio.Future()
        self._transport = None
        self._transport_info = None
        self.id = SmartMeterProtocol.connections
        SmartMeterProtocol.connections += 1

    def _set_transport_info(self):
        if self._transport:
            if hasattr(self._transport, "serial"):
                self._transport_info = str(self._transport.serial)
            else:
                peer_name = self._transport.get_extra_info("peername")
                if peer_name:
                    host, port = peer_name
                    self._transport_info = "host {} and port {}".format(host, port)

            if not self._transport_info:
                self._transport_info = str(self._transport)

    def connection_made(self, transport):
        """Called when a connection is made.

        The argument is the transport representing the connection.
        To receive data, wait for data_received() calls.
        When the connection is closed, connection_lost() is called.
        """
        self._transport = transport
        self._set_transport_info()
        _LOGGER.info(
            "%s: Smart meter connected to %s", self._instance_id(), self._transport_info
        )

    def connection_lost(self, exc):
        """Called when the connection is lost or closed.

        The argument is an exception object or None (the latter
        meaning a regular EOF is received or the connection was
        aborted or closed).
        """
        if exc:
            _LOGGER.exception(
                "%s: Connection to %s lost: %s",
                self._instance_id(),
                self._transport_info,
                exc,
            )
        else:
            _LOGGER.debug(
                "%s: Connection to %s closed.",
                self._instance_id(),
                self._transport_info,
            )

        try:
            self._transport.close()
            self._transport = None
        except Exception as ex:
            _LOGGER.warning(
                "%s: Error when closing transport %s for %s connection: %s",
                self._instance_id(),
                self._transport_info,
                "lost" if exc else "closed",
                ex,
            )

        if self.done:
            self.done.set_result(True)
            self.done = None

    def data_received(self, data):
        """Called when some data is received.

        The argument is a bytes object.
        """
        frames = self._frame_reader.read(data)
        for frame in frames:
            self.queue.put_nowait(frame)

    def eof_received(self):
        """Called when the other end signals it won’t send any more data"""
        _LOGGER.debug(
            "%s: eof_received - the other end (%s) signaled it won’t send any more data. Close transport.",
            self._instance_id(),
            self._transport_info,
        )

        # return false to close transport.
        return False

    def _instance_id(self):
        return f"{__class__.__name__}[{self.id}]"


class BackOffStrategy(metaclass=ABCMeta):
    @abstractmethod
    def failure(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @property
    @abstractmethod
    def current_delay_sec(self):
        pass


class ExponentialBackOff(BackOffStrategy):
    DEFAULT_MAX_DELAY_SEC = 60

    def __init__(self):
        self._delay = 0
        self.max_delay = ExponentialBackOff.DEFAULT_MAX_DELAY_SEC

    def failure(self):
        self._delay = self._delay * 2
        if self._delay == 0:
            self._delay = 1

        return self._delay if self._delay < self.max_delay else self.max_delay

    def reset(self):
        self._delay = 0

    @property
    def current_delay_sec(self):
        return self._delay


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
            [], Tuple[asyncio.Transport, SmartMeterProtocol]
        ] = connection_factory
        self._connection: Optional[Tuple[asyncio.Transport, SmartMeterProtocol]] = None
        self._is_closing: asyncio.Event = asyncio.Event()
        self.back_off = ExponentialBackOff()

    async def connect_loop(self):
        """
        Connect to meter using connection factory, and keep reconnecting if connection is lost.
        The connection is not reconnected on connection loss if close() was called on this instance.
        """
        while not self._is_closing.is_set():
            await asyncio.wait(
                [self._try_connect(), self._is_closing.wait()],
                return_when=FIRST_COMPLETED,
            )

            if self._connection:
                _, protocol = self._connection
                await asyncio.wait(
                    [protocol.done, self._is_closing.wait()],
                    return_when=FIRST_COMPLETED,
                )

                if not self._is_closing.is_set():
                    _LOGGER.warning("Smart meter connection lost.")

                self._connection = None

        # done closing if that was the case of connection loss
        self._is_closing.clear()

        _LOGGER.info("Connect loop done.")

    async def _try_connect(self):
        if self.back_off.current_delay_sec > 0:
            _LOGGER.info(
                "Back-off for %d sec before reconnecting to smart meter.",
                self.back_off.current_delay_sec,
            )
            await asyncio.sleep(self.back_off.current_delay_sec)

        if not self._is_closing.is_set():
            try:
                _LOGGER.debug("Try to connect to smart meter.")
                self._connection = await self._connection_factory()
                self.back_off.reset()
            except asyncio.CancelledError:
                raise
            except Exception as ex:
                self._connection = None
                self.back_off.failure()
                _LOGGER.warning("Error connecting to smart meter: %s", ex)

    def close(self):
        """Close current connection, if any, and stop reconnecting."""
        self._is_closing.set()
        if self._connection:
            _LOGGER.info("Close connection and abort connect loop.")
            transport, _ = self._connection
            transport.close()
            self._connection = None


async def create_meter_serial_connection(
    loop, queue: asyncio.Queue, *args, **kwargs
) -> Tuple[serial_asyncio.SerialTransport, SmartMeterProtocol]:
    """
    Create serial connection using :class:`SmartMeterProtocol`

    :param loop: The event handler
    :param queue: Queue for received frames
    :param args: Passed to the :class:`serial.Serial` init function
    :param kwargs: Passed to the :class:`serial.Serial` init function
    :return: Tuple of transport and protocol
    """
    return await serial_asyncio.create_serial_connection(
        loop, lambda: SmartMeterProtocol(queue), *args, **kwargs
    )


async def create_meter_tcp_connection(
    loop, queue: asyncio.Queue, *args, **kwargs
) -> Tuple[asyncio.Transport, SmartMeterProtocol]:
    """
    Create TCP connection using :class:`SmartMeterProtocol`

    :param loop: The event handler
    :param queue: Queue for received frames
    :param args: Passed to the :class:`loop.create_connection`
    :param kwargs: Passed to the :class:`loop.create_connection`
    :return: Tuple of transport and protocol
    """
    return await loop.create_connection(
        lambda: SmartMeterProtocol(queue), *args, **kwargs
    )
