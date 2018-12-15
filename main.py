import argparse
import asyncio
import logging
import hdlc
import decode
import sys

parser = argparse.ArgumentParser('debugging asyncio')
parser.add_argument('-v', dest='verbose', default=False)
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=sys.stderr,
)
LOG = logging.getLogger('')


async def read_task():

    dest_ip = '192.168.1.10'
    socket_reader, socket_writer = await asyncio.open_connection(dest_ip, 3001)
    LOG.info('Connected to ' + dest_ip)


    frame_reader = hdlc.HdlcOctetStuffedFrameReader()

    while True:
        data = await socket_reader.read(1024)
        frames = frame_reader.read(data)

        for frame in frames:
            queue.put_nowait(frame)

    # close connection
    socket_reader.close()
    socket_writer.close()


async def process_frames():
    while True:
        frame = await queue.get()
        msg = decode.LlcPdu.parse(frame.information)

        #print(msg)
        print(f"{msg.meter_data.meter_ts}: {msg.meter_data.data.pwr_act_pos} W")
        try:
            print(f"Current: {msg.data.IL1} A")
            print(f"Voltage: {msg.data.ULN1} V")
            print(f"Reactive: {msg.data.pwr_react_neg} VAr")
        except AttributeError:
            pass

queue = asyncio.Queue()

loop = asyncio.get_event_loop()

if args.verbose:
    loop.set_debug(True)

try:
    asyncio.ensure_future(read_task())
    asyncio.ensure_future(process_frames())
    loop.run_forever()
except KeyboardInterrupt:
    pass
finally:
    print("Closing Loop")
    loop.close()
