import argparse
import datetime
import json
import logging
import signal
import sys
import time
import asyncio
import serial_asyncio


from smartmeterdecode import hdlc, autodecoder

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
        frame = await queue.get()
        hdlc_frame_received(frame)


async def read_task(args, queue):

    frame_reader = hdlc.HdlcFrameReader(False)
    reader, writer = await serial_asyncio.open_serial_connection(url=args.serialport)

    while True:
        data = await reader.read(1024)
        frames = frame_reader.read(data)
        if len(frames):
            for f in frames:
                await queue.put(f)

    reader.close()
    writer.close()


def main():
    args = get_arg_parser().parse_args()

    queue = asyncio.Queue()

    asyncio.ensure_future(read_task(args, queue))
    asyncio.ensure_future(process_frames(queue))

    loop = asyncio.get_event_loop()
    loop.run_forever()


if __name__ == "__main__":
    main()
