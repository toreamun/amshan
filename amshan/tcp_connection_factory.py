"""TCP/IP connection factory."""
from asyncio import AbstractEventLoop, BaseProtocol, get_event_loop
from asyncio import Queue  # pylint: disable=unused-import
from typing import Optional, cast

from amshan.hdlc import HdlcFrame  # pylint: disable=unused-import
from amshan.meter_connection import (
    MeterTransportProtocol,
    SmartMeterFrameContentProtocol,
    SmartMeterFrameProtocol,
)


async def create_tcp_frame_connection(
    queue: "Queue[HdlcFrame]",
    loop: Optional[AbstractEventLoop],
    *args,
    **kwargs,
) -> MeterTransportProtocol:
    """
    Create TCP connection using SmartMeterFrameProtocol.

    :param queue: Queue for received frames
    :param loop: The event handler
    :param args: Passed to the loop.create_connection
    :param kwargs: Passed to the loop.create_connection
    :return: Tuple of transport and protocol
    """
    loop = loop if loop else get_event_loop()
    return cast(
        MeterTransportProtocol,
        await loop.create_connection(
            lambda: cast(BaseProtocol, SmartMeterFrameProtocol(queue)),
            *args,
            **kwargs,
        ),
    )


async def create_tcp_frame_content_connection(
    queue: "Queue[bytes]",
    loop: Optional[AbstractEventLoop],
    *args,
    **kwargs,
) -> MeterTransportProtocol:
    """
    Create TCP connection using SmartMeterFrameContentProtocol.

    :param queue: Queue for received frames
    :param loop: The event handler
    :param args: Passed to the loop.create_connection
    :param kwargs: Passed to the loop.create_connection
    :return: Tuple of transport and protocol
    """
    loop = loop if loop else get_event_loop()
    return cast(
        MeterTransportProtocol,
        await loop.create_connection(
            lambda: cast(BaseProtocol, SmartMeterFrameContentProtocol(queue)),
            *args,
            **kwargs,
        ),
    )
