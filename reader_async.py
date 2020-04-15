import argparse
import asyncio
import datetime
import json
import logging
import signal
import sys
import typing
from asyncio import BaseProtocol, Queue
from typing import Any, Optional, Tuple

import serial_asyncio

from smartmeterdecode import autodecoder, hdlc, meter_connection
from smartmeterdecode.meter_connection import (AsyncConnectionFactory,
                                               MeterTransportProtocol,
                                               SmartMeterProtocol)

logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)7s: %(message)s", stream=sys.stderr,
)
LOG = logging.getLogger("")


def get_arg_parser() -> argparse.ArgumentParser:
    def valid_host_port(s: str) -> Tuple[str, str]:
        host_and_port = s.split(":")
        if len(host_and_port) == 2:
            return host_and_port[0], host_and_port[1]
        else:
            msg = f"Not a valid host and port: '{s}'."
            raise argparse.ArgumentTypeError(msg)

    parser = argparse.ArgumentParser("read HAN port")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-host",
        dest="hostandport",
        type=valid_host_port,
        help="input host and port separated by :",
    )
    group.add_argument("-serial", dest="serialdevice", help="input serial port")

    parser.add_argument(
        "-sp",
        dest="ser_parity",
        default="N",
        required=False,
        choices=["N", "O", "E"],
        help="input serial port parity",
    )
    parser.add_argument(
        "-sb",
        dest="ser_baudrate",
        default=2400,
        type=int,
        required=False,
        help="input serial port baud rate",
    )
    parser.add_argument("-mh", dest="mqtthost", default="localhost", help="mqtt host")
    parser.add_argument(
        "-mp", dest="mqttport", type=int, default=1883, help="mqtt port port"
    )
    parser.add_argument(
        "-t", dest="mqtttopic", default="han", help="mqtt publish topic"
    )
    parser.add_argument(
        "-dumpfile", dest="dumpfile", help="dump received bytes to file"
    )
    parser.add_argument(
        "-r",
        dest="reconnect",
        type=bool,
        default=True,
        help="automatic retry/reconnect meter connection",
    )
    parser.add_argument("-v", dest="verbose", default=False)
    return parser


def json_converter(o: Any) -> Optional[str]:
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    return None


_decoder = autodecoder.AutoDecoder()


def hdlc_frame_received(frame: hdlc.HdlcFrame) -> None:
    if frame.is_good_ffc and frame.is_expected_length:
        if frame.information:
            LOG.debug("Got frame info content: %s", frame.information.hex())
            decoded_frame = _decoder.decode_frame(frame.information)
            if decoded_frame:
                json_frame = json.dumps(decoded_frame, default=json_converter)
                LOG.debug("Decoded frame: %s", json_frame)
            else:
                LOG.error("Could not decode frame: %s", frame.frame_data.hex())
        else:
            LOG.debug("Got empty frame")
    else:
        LOG.warning("Got invalid frame: %s", frame.frame_data.hex())


async def process_frames(queue: 'Queue[hdlc.HdlcFrame]') -> None:
    while True:
        frame = await queue.get()
        hdlc_frame_received(frame)


async def main() -> None:
    args = get_arg_parser().parse_args()
    loop = asyncio.get_event_loop()

    queue: Queue[hdlc.HdlcFrame] = Queue()

    asyncio.create_task(process_frames(queue))

    async def tcp_connection_factory() -> MeterTransportProtocol:
        host, port = args.hostandport
        connection = await loop.create_connection(
            lambda: typing.cast(BaseProtocol, SmartMeterProtocol(queue)),
            host=host,
            port=port,
        )
        return typing.cast(MeterTransportProtocol, connection)

    async def serial_connection_factory() -> MeterTransportProtocol:
        connection = await serial_asyncio.create_serial_connection(
            loop,
            lambda: SmartMeterProtocol(queue),
            url=args.serialdevice,
            baudrate=args.ser_baudrate,
            parity=args.ser_parity,
        )
        return typing.cast(MeterTransportProtocol, connection)

    connection_factory: AsyncConnectionFactory = (
        serial_connection_factory if args.serialdevice else tcp_connection_factory
    )

    if args.reconnect:
        # use high-level ConnectionManager
        connection_manager = meter_connection.ConnectionManager(connection_factory)
        loop.add_signal_handler(signal.SIGINT, connection_manager.close)
        await connection_manager.connect_loop()
    else:
        # use low-level transport and protocol
        transport, protocol = await connection_factory()
        loop.add_signal_handler(signal.SIGINT, transport.close)
        await protocol.done

    LOG.info("Done...")


if __name__ == "__main__":
    asyncio.run(main())
