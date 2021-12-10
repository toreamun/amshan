"""Serial connection factory."""
from asyncio import AbstractEventLoop, get_event_loop
from asyncio import Queue  # pylint: disable=unused-import
from typing import Optional, cast

import serial_asyncio  # type: ignore

from amshan.hdlc import HdlcFrame  # pylint: disable=unused-import
from amshan.meter_connection import (
    MeterTransportProtocol,
    SmartMeterFrameContentProtocol,
    SmartMeterFrameProtocol,
)


async def create_serial_frame_connection(
    queue: "Queue[HdlcFrame]",
    loop: Optional[AbstractEventLoop],
    *args,
    **kwargs,
) -> MeterTransportProtocol:
    """
    Create serial connection using SmartMeterFrameProtocol.

    :param queue: Queue for received frames
    :param loop: The event handler
    :param args: Passed to serial_asyncio.create_serial_connection and further to serial.Serial init function
    :param kwargs: Passed to serial_asyncio.create_serial_connection and further the serial.Serial init function
    :return: Tuple of transport and protocol
    """
    return cast(
        MeterTransportProtocol,
        await serial_asyncio.create_serial_connection(
            loop if loop else get_event_loop(),
            lambda: SmartMeterFrameProtocol(queue),
            *args,
            **kwargs,
        ),
    )


async def create_serial_frame_content_connection(
    queue: "Queue[bytes]",
    loop: Optional[AbstractEventLoop],
    *args,
    **kwargs,
) -> MeterTransportProtocol:
    """Create serial connection using SmartMeterFrameContentProtocol.

    :param queue: Queue for received frames
    :param loop: The event handler
    :param args: Passed to serial_asyncio.create_serial_connection and further to serial.Serial init function
    :param kwargs: Passed to serial_asyncio.create_serial_connection and further the serial.Serial init function
    :return: Tuple of transport and protocol
    """
    return cast(
        MeterTransportProtocol,
        await serial_asyncio.create_serial_connection(
            loop if loop else get_event_loop(),
            lambda: SmartMeterFrameContentProtocol(queue),
            *args,
            **kwargs,
        ),
    )
