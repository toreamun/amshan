import argparse
import asyncio
import logging

from readams.meterdecode import hdlc
from readams.meterdecode import aidon
import sys
import signal
from hbmqtt.client import MQTTClient

parser = argparse.ArgumentParser('debugging asyncio')
parser.add_argument('-v', dest='verbose', default=False)
parser.add_argument('-sourceip', required=True)
parser.add_argument('-mqtturl', required=True)
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=sys.stderr,
)
LOG = logging.getLogger('')


async def read_task(queue, source_ip):

    socket_reader, socket_writer = await asyncio.open_connection(source_ip, 3001)
    LOG.info('Connected to ' + source_ip)

    new_packet = lambda x: queue.put_nowait(x)
    frame_reader = hdlc.HdlcOctetStuffedFrameReader(new_packet)

    while True:
        data = await socket_reader.read(1024)
        frame_reader.read(data)

    # close connection
    socket_reader.close()
    socket_writer.close()


async def process_frames(queue, mqtt_url):
    mqtt = MQTTClient()
    await mqtt.connect(mqtt_url)

    while True:
        frame = await queue.get()

        await mqtt.publish('ams/frame', frame.information)

        msg = aidon.LlcPdu.parse(frame.information)

        #print(msg)

        print(f"{msg.meter_data.meter_ts}: {msg.meter_data.data.pwr_act_pos} W")
        try:
            print(f"Current: {msg.data.IL1} A")
            print(f"Voltage: {msg.data.ULN1} V")
            print(f"Reactive: {msg.data.pwr_react_neg} VAr")
        except AttributeError:
            pass


async def handle_exception(coro, loop):
    try:
        await coro
    except Exception as ex:
        logging.exception('Caught exception')
    loop.stop()


async def shutdown(signal, loop):
    logging.info(f'Received exit signal {signal.name}...')
    logging.info('Closing database connections')
    logging.info('Nacking outstanding messages')
    tasks = [t for t in asyncio.Task.all_tasks() if t is not
             asyncio.Task.current_task()]

    [task.cancel() for task in tasks]

    logging.info('Canceling outstanding tasks')
    await asyncio.gather(*tasks)
    loop.stop()
    logging.info('Shutdown complete.')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    if args.verbose:
        loop.set_debug(True)

    # May want to catch other signals too
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: loop.create_task(shutdown(s, loop)))

    queue = asyncio.Queue()
    publisher_coro = handle_exception(read_task(queue, args.sourceip), loop)
    consumer_coro = handle_exception(process_frames(queue, args.mqtturl), loop)

    try:
        loop.create_task(publisher_coro)
        loop.create_task(consumer_coro)
        loop.run_forever()
    finally:
        logging.info('Cleaning up')
        loop.stop()