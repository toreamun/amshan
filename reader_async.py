import argparse
import asyncio
import datetime
import json
import logging
import sys

import serial_asyncio

from smartmeterdecode import hdlc, autodecoder, connection

logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)7s: %(message)s", stream=sys.stderr,
)
LOG = logging.getLogger("")


def get_arg_parser():
    parser = argparse.ArgumentParser("read HAN port")
    parser.add_argument("-v", dest="verbose", default=False)
    parser.add_argument(
        "-s", dest="serialport", required=True, help="input serial port"
    )
    parser.add_argument(
        "-sp",
        dest="ser_parity",
        required=False,
        choices=["N", "O", "E"],
        help="input serial port parity",
    )
    parser.add_argument(
        "-sb",
        dest="ser_baudrate",
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
    return parser


def json_converter(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    return None


def hdlc_frame_received(frame: hdlc.HdlcFrame):
    decoder = autodecoder.AutoDecoder()
    if frame.is_good_ffc and frame.is_expected_length:
        LOG.debug("Got frame info content: %s", frame.information.hex())
        decoded_frame = decoder.decode_frame(frame.information)
        if decoded_frame:
            json_frame = json.dumps(decoded_frame, default=json_converter)
            LOG.debug("Decoded frame: %s", json_frame)
        else:
            LOG.error("Could not decode frame: %s", frame.frame_data.hex())
    else:
        LOG.warning("Got invalid frame: %s", frame.frame_data.hex())


async def process_frames(queue):
    while True:
        try:
            frame = await queue.get()
            hdlc_frame_received(frame)
        except Exception as ex:
            LOG.error(ex)
            raise


async def read(args, queue):
    frame_reader = hdlc.HdlcFrameReader(False)

    try:
        reader, writer = await serial_asyncio.open_serial_connection(
            url=args.serialport
        )

        while True:
            data = await reader.read(1024)
            frames = frame_reader.read(data)
            if len(frames):
                for f in frames:
                    await queue.put(f)

        reader.close()
        writer.close()
    except Exception as ex:
        LOG.error(ex)
        raise


async def main():
    args = get_arg_parser().parse_args()

    queue = asyncio.Queue()

    loop = asyncio.get_event_loop()

    def tcp_connection_factory(): return connection.create_meter_tcp_connection(
        loop, queue, host="ustaoset.amundsen.org", port="3001"
    )

    def serial_connection_factory(): return connection.create_meter_serial_connection(
        loop, queue, url=args.serialport
    )

    connection = connection.SmartMeterConnection(tcp_connection_factory)

    await asyncio.gather(
        asyncio.create_task(process_frames(queue)), connection.connect()
    )

    #    on_con_lost = loop.create_future()
    #    reader_factory = SmartMeterReader.create_reader_factory(queue, on_con_lost)
    # serial_asyncio.open_serial_connection()
    #    transport, protocol = await serial_asyncio.create_serial_connection(loop, lambda: SmartMeterReader(queue, on_con_lost), url=args.serialport)
    #    loop.run_until_complete(reader)
    #    transport, protocol = await create_meter_serial_connection(loop, queue, url=args.serialport)
    #    connection_factory = smasyncio.create_meter_tcp_connection(loop, queue, host="ustaoset.amundsen.org", port="3001")
    #    reader_task = asyncio.create_task(reader)
    #    await reader_task
    #    await asyncio.create_task(process_frames(queue))
    #    await reader
    # transport.close()
    #    res = await asyncio.wait(
    #        [protocol.on_connection_lost, asyncio.create_task(process_frames(queue))],
    #        return_when=asyncio.FIRST_COMPLETED,
    #    )

    LOG.info("Done...")


if __name__ == "__main__":
    asyncio.run(main())
