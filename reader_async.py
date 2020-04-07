import argparse
import asyncio
import concurrent
import datetime
import json
import logging
import socket
import sys

import serial_asyncio
from serial import PARITY_NONE

from smartmeterdecode import autodecoder, hdlc, meter_connection, obis_map

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


async def get_meter_info(queue):
    decoder = autodecoder.AutoDecoder()
    for _ in range(10):
        frame = await asyncio.wait_for(queue.get(), 12)
        if frame.is_good_ffc and frame.is_expected_length:
            decoded_frame = decoder.decode_frame(frame.information)
            if decoded_frame:
                if (
                    obis_map.NEK_HAN_FIELD_METER_ID in decoded_frame
                    and obis_map.NEK_HAN_FIELD_METER_MANUFACTURER
                ):
                    return (
                        decoded_frame[obis_map.NEK_HAN_FIELD_METER_MANUFACTURER],
                        decoded_frame[obis_map.NEK_HAN_FIELD_METER_ID]
                    )
    raise TimeoutError()


async def main():
    args = get_arg_parser().parse_args()

    queue = asyncio.Queue()


    loop = asyncio.get_event_loop()

    host = "ustaoset.amundsen.org"
    port = 3001

    #    await asyncio.wait_for(loop.sock_connect(sock, address),timeout=1)

    # try:
    #     transport, protocol = await loop.create_connection(
    #         lambda: meter_connection.SmartMeterProtocol(queue),
    #         host=host,
    #         port=port,
    #     )
    # except TimeoutError as ex:
    #     LOG.exception("con")
    #     pass
    #
    # async def read_queue():
    #     while True:
    #         await queue.get()
    #         LOG.debug("Got frame from queue")
    #
    # read_queue_task = asyncio.create_task(read_queue())
    #
    # await asyncio.sleep(15)
    #
    # transport.close()
    #
    # await asyncio.sleep(2)
    #
    # await read_queue_task


#    meter_info = await get_meter_info(queue)
#    LOG.debug(meter_info)

    #    c = await serial_asyncio.open_serial_connection(url = "/dev/tty01", baudrate=2400, parity="E", bytesize=8)

    def tcp_connection_factory():
        return meter_connection.create_meter_tcp_connection(
            loop, queue, host="ustaoset.amundsen.org", port="3001"
        )

    def serial_connection_factory():
        return meter_connection.create_meter_serial_connection(
            loop, queue, url=args.serialport)

    connection = meter_connection.SmartMeterConnection(tcp_connection_factory)

    asyncio.create_task(process_frames(queue))

    connect_task = asyncio.create_task(connection.connect_loop())

    await asyncio.sleep(8)

    connection.close()

    await asyncio.sleep(2000)


    LOG.info("Done...")


if __name__ == "__main__":
    asyncio.run(main())
