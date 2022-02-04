"""TCP/IP connection factory."""
from __future__ import annotations

from asyncio import Queue  # pylint: disable=unused-import
from asyncio import AbstractEventLoop, BaseProtocol, get_event_loop
from typing import Sequence, cast

from han.common import MeterMessageBase  # pylint: disable=unused-import
from han.common import MeterReaderBase
from han.dlde import ModeDReader
from han.hdlc import HdlcFrameReader
from han.meter_connection import (
    MeterTransportProtocol,
    SmartMeterMessagePayloadProtocol,
    SmartMeterMessageProtocol,
)


async def create_tcp_message_connection(
    queue: "Queue[MeterMessageBase]",
    loop: AbstractEventLoop | None,
    readers: Sequence[MeterReaderBase] | None,
    *args,
    **kwargs,
) -> MeterTransportProtocol:
    """
    Create TCP connection using SmartMeterMessageProtocol.

    :param queue: Queue for received data readouts
    :param loop: The event handler
    :param readers: message reader(s).
    :param args: Passed to the loop.create_connection
    :param kwargs: Passed to the loop.create_connection
    :return: Tuple of transport and protocol
    """
    loop = loop if loop else get_event_loop()
    return cast(
        MeterTransportProtocol,
        await loop.create_connection(
            lambda: cast(
                BaseProtocol,
                SmartMeterMessageProtocol(
                    queue,
                    readers
                    if readers
                    else [
                        HdlcFrameReader(
                            use_octet_stuffing=False, use_abort_sequence=True
                        ),
                        ModeDReader(),
                    ],
                ),
            ),
            *args,
            **kwargs,
        ),
    )


async def create_tcp_message_payload_connection(
    queue: "Queue[bytes]",
    loop: AbstractEventLoop | None,
    readers: Sequence[MeterReaderBase] | None,
    *args,
    **kwargs,
) -> MeterTransportProtocol:
    """
    Create TCP connection using SmartMeterMessagePayloadProtocol.

    :param queue: Queue for received data readout content
    :param loop: The event handler
    :param readers: message reader(s).
    :param args: Passed to the loop.create_connection
    :param kwargs: Passed to the loop.create_connection
    :return: Tuple of transport and protocol
    """
    loop = loop if loop else get_event_loop()
    return cast(
        MeterTransportProtocol,
        await loop.create_connection(
            lambda: cast(
                BaseProtocol,
                SmartMeterMessagePayloadProtocol(
                    queue,
                    readers
                    if readers
                    else [
                        HdlcFrameReader(
                            use_octet_stuffing=False, use_abort_sequence=True
                        ),
                        ModeDReader(),
                    ],
                ),
            ),
            *args,
            **kwargs,
        ),
    )
