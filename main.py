import argparse
import asyncio
import logging
import hdlc
import decode
import sys
import signal

parser = argparse.ArgumentParser('debugging asyncio')
parser.add_argument('-v', dest='verbose', default=False)
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=sys.stderr,
)
LOG = logging.getLogger('')


async def read_task(queue):

    dest_ip = '192.168.1.10'
    socket_reader, socket_writer = await asyncio.open_connection(dest_ip, 3001)
    LOG.info('Connected to ' + dest_ip)

    frame_reader = hdlc.HdlcOctetStuffedFrameReader(queue)

    while True:
        data = await socket_reader.read(1024)
        frame_reader.read(data)

    # close connection
    socket_reader.close()
    socket_writer.close()


async def process_frames(queue):
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
    tasks = [t for t in asyncio.all_tasks() if t is not
             asyncio.current_task()]

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
            s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    queue = asyncio.Queue()
    publisher_coro = handle_exception(read_task(queue), loop)
    consumer_coro = handle_exception(process_frames(queue), loop)

    try:
        loop.create_task(publisher_coro)
        loop.create_task(consumer_coro)
        loop.run_forever()
    finally:
        logging.info('Cleaning up')
        loop.stop()