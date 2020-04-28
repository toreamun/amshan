import asyncio

import typing
from typing import Optional
from asyncio import BaseProtocol, AbstractEventLoop

from smartmeterdecode.meter_connection import (
    SmartMeterFrameContentProtocol,
    MeterTransportProtocol,
    SmartMeterFrameProtocol,
)


async def create_tcp_frame_connection(
    queue: "Queue[hdlc.HdlcFrame]", loop: Optional[AbstractEventLoop], *args, **kwargs,
) -> MeterTransportProtocol:
    """
    Create TCP connection using SmartMeterFrameProtocol.

    :param queue: Queue for received frames
    :param loop: The event handler
    :param args: Passed to the loop.create_connection
    :param kwargs: Passed to the loop.create_connection
    :return: Tuple of transport and protocol
    """
    loop = loop if loop else asyncio.get_event_loop()
    return await loop.create_connection(
        lambda: typing.cast(BaseProtocol, SmartMeterFrameProtocol(queue)),
        *args,
        **kwargs,
    )


async def create_tcp_frame_content_connection(
    queue: "Queue[bytes]", loop: Optional[AbstractEventLoop], *args, **kwargs,
) -> MeterTransportProtocol:
    """
    Create TCP connection using SmartMeterFrameContentProtocol.

    :param queue: Queue for received frames
    :param loop: The event handler
    :param args: Passed to the loop.create_connection
    :param kwargs: Passed to the loop.create_connection
    :return: Tuple of transport and protocol
    """
    loop = loop if loop else asyncio.get_event_loop()
    return await loop.create_connection(
        lambda: typing.cast(BaseProtocol, SmartMeterFrameContentProtocol(queue)),
        *args,
        **kwargs,
    )
