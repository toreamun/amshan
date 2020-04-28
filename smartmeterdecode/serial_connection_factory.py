import asyncio
from asyncio import AbstractEventLoop
from typing import Optional

import serial_asyncio

from smartmeterdecode.meter_connection import (
    MeterTransportProtocol,
    SmartMeterFrameProtocol,
    SmartMeterFrameContentProtocol,
)


async def create_serial_frame_connection(
    queue: "Queue[hdlc.HdlcFrame]", loop: Optional[AbstractEventLoop], *args, **kwargs,
) -> MeterTransportProtocol:
    """
    Create serial connection using SmartMeterFrameProtocol

    :param queue: Queue for received frames
    :param loop: The event handler
    :param args: Passed to serial_asyncio.create_serial_connection and further to serial.Serial init function
    :param kwargs: Passed to serial_asyncio.create_serial_connection and further the serial.Serial init function
    :return: Tuple of transport and protocol
    """
    return await serial_asyncio.create_serial_connection(
        loop if loop else asyncio.get_event_loop(),
        lambda: SmartMeterFrameProtocol(queue),
        *args,
        **kwargs,
    )


async def create_serial_frame_content_connection(
    queue: "Queue[bytes]", loop: Optional[AbstractEventLoop], *args, **kwargs,
) -> MeterTransportProtocol:
    """
    Create serial connection using SmartMeterFrameContentProtocol

    :param queue: Queue for received frames
    :param loop: The event handler
    :param args: Passed to serial_asyncio.create_serial_connection and further to serial.Serial init function
    :param kwargs: Passed to serial_asyncio.create_serial_connection and further the serial.Serial init function
    :return: Tuple of transport and protocol
    """
    return await serial_asyncio.create_serial_connection(
        loop if loop else asyncio.get_event_loop(),
        lambda: SmartMeterFrameContentProtocol(queue),
        *args,
        **kwargs,
    )
