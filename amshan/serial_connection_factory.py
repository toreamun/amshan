"""Serial connection factory."""
from __future__ import annotations

from asyncio import Queue  # pylint: disable=unused-import
from asyncio import AbstractEventLoop, get_event_loop
from typing import Sequence, cast

import serial_asyncio  # type: ignore

from amshan.common import MeterMessageBase  # pylint: disable=unused-import
from amshan.common import MeterReaderBase
from amshan.dlde import ModeDReader
from amshan.hdlc import HdlcFrameReader
from amshan.meter_connection import (
    MeterTransportProtocol,
    SmartMeterMessagePayloadProtocol,
    SmartMeterMessageProtocol,
)


async def create_serial_message_connection(
    queue: "Queue[MeterMessageBase]",
    loop: AbstractEventLoop | None,
    readers: Sequence[MeterReaderBase] | None,
    *args,
    **kwargs,
) -> MeterTransportProtocol:
    """
    Create serial connection using SmartMeterMessageProtocol.

    :param queue: Queue for received data readouts
    :param loop: The event handler
    :param readers: message reader(s). Passing None means all.
    :param args: Passed to serial_asyncio.create_serial_connection and further to serial.Serial init function
    :param kwargs: Passed to serial_asyncio.create_serial_connection and further the serial.Serial init function
    :return: Tuple of transport and protocol
    """
    return cast(
        MeterTransportProtocol,
        await serial_asyncio.create_serial_connection(
            loop if loop else get_event_loop(),
            lambda: SmartMeterMessageProtocol(
                queue,
                readers
                if readers
                else [
                    HdlcFrameReader(use_octet_stuffing=False, use_abort_sequence=True),
                    ModeDReader(),
                ],
            ),
            *args,
            **kwargs,
        ),
    )


async def create_serial_message_payload_connection(
    queue: "Queue[bytes]",
    loop: AbstractEventLoop | None,
    readers: Sequence[MeterReaderBase] | None,
    *args,
    **kwargs,
) -> MeterTransportProtocol:
    """Create serial connection using SmartMeterMessagePayloadProtocol.

    :param queue: Queue for received data readout content
    :param loop: The event handler
    :param readers: message reader(s). Passing None means all.
    :param args: Passed to serial_asyncio.create_serial_connection and further to serial.Serial init function
    :param kwargs: Passed to serial_asyncio.create_serial_connection and further the serial.Serial init function
    :return: Tuple of transport and protocol
    """
    return cast(
        MeterTransportProtocol,
        await serial_asyncio.create_serial_connection(
            loop if loop else get_event_loop(),
            lambda: SmartMeterMessagePayloadProtocol(
                queue,
                readers
                if readers
                else [
                    HdlcFrameReader(use_octet_stuffing=False, use_abort_sequence=True),
                    ModeDReader(),
                ],
            ),
            *args,
            **kwargs,
        ),
    )
