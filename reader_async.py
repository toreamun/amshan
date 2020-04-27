import argparse
import asyncio
import datetime
import json
import logging
import signal
import sys
from asyncio import Queue
from typing import Any, Optional, Tuple

from smartmeterdecode import autodecoder
from smartmeterdecode.meter_connection import (
    AsyncConnectionFactory,
    ConnectionManager,
    MeterTransportProtocol,
)
from smartmeterdecode.serial_connection_factory import (
    create_serial_frame_content_connection,
)
from smartmeterdecode.tcp_connection_factory import create_tcp_frame_content_connection

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


def measure_received(frame: bytearray) -> None:
    decoded_frame = _decoder.decode_frame(frame)
    if decoded_frame:
        json_frame = json.dumps(decoded_frame, default=json_converter)
        LOG.debug("Decoded frame: %s", json_frame)
    else:
        LOG.error("Could not decode frame content: %s", frame.hex())


async def process_frames(queue: "Queue[bytearray]") -> None:
    while True:
        frame = await queue.get()
        measure_received(frame)


async def main() -> None:
    args = get_arg_parser().parse_args()
    loop = asyncio.get_event_loop()

    queue: Queue[bytearray] = Queue()

    asyncio.create_task(process_frames(queue))

    async def tcp_connection_factory() -> MeterTransportProtocol:
        host, port = args.hostandport
        return await create_tcp_frame_content_connection(queue, loop, host, port)

    async def serial_connection_factory() -> MeterTransportProtocol:
        return await create_serial_frame_content_connection(
            queue,
            loop=loop,
            url=args.serialdevice,
            baudrate=args.ser_baudrate,
            parity=args.ser_parity,
        )

    connection_factory: AsyncConnectionFactory = (
        serial_connection_factory if args.serialdevice else tcp_connection_factory
    )

    if args.reconnect:
        # use high-level ConnectionManager
        connection_manager = ConnectionManager(connection_factory)
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
