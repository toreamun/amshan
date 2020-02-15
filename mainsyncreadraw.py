import argparse
import datetime
import json
import logging
import signal
import sys

import paho.mqtt.client as mqtt
import serial

from meterdecode import hdlc, autodecoder

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=sys.stderr,
)
LOG = logging.getLogger('')


def get_arg_parser():
    parser = argparse.ArgumentParser('read HAN port')
    parser.add_argument('-v', dest='verbose', default=False)
    parser.add_argument('-s', dest='serialport', required=True, help="input serial port")
    parser.add_argument('-mh', dest='mqtthost', default='localhost', help="mqtt host")
    parser.add_argument('-mp', dest='mqttport', type=int, default=1883, help="mqtt port port")
    parser.add_argument('-t', dest='mqtttopic', default='han', help="mqtt publish topic")
    parser.add_argument('-dumpfile', dest='dumpfile', help="dump received bytes to file")
    #    parser.add_argument('-sourceip', required=True)
    #    parser.add_argument('-mqtturl', required=True)
    return parser


def frame_received(frame: hdlc.HdlcFrame):
    if frame.is_good:
        LOG.debug("Got frame info content: %s", frame.information.hex())
        decoded_frame = decoder.decode_frame(frame.information)
        if decoded_frame:
            json_frame = json.dumps(decoded_frame, default=_json_converter)
            LOG.debug("Decoded frame: %s", json_frame)
            mqttc.publish(args.mqtttopic, json_frame)
        else:
            LOG.error("Could not decode frame: %s", frame.frame_data.hex())

    else:
        LOG.warning("Got invalid frame: %s", frame.frame_data.hex())


def _json_converter(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()
    return None


def handler(signal_received, frame):
    # Handle any cleanup here
    LOG.info('SIGINT or CTRL-C detected. Exiting gracefully')
    mqttc.loop_stop()
    ser.close()
    logfile.close()
    exit(0)


def dump_to_file(dump_data: bytes):
    for b in dump_data:
        is_flag = b == b'\x7e'[0]
        if is_flag:
            logfile.write('\n')
        logfile.write('{:02x}'.format(b))
        if is_flag:
            logfile.write('\n')


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handler)

    args = get_arg_parser().parse_args()

    if args.dumpfile:
        logfile = open(args.dumpfile, "w+")

    decoder = autodecoder.AutoDecoder()
    frame_reader = hdlc.HdlcOctetStuffedFrameReader()

    mqttc = mqtt.Client()
    mqttc.enable_logger(LOG)
    mqttc.connect(args.mqtthost, port=args.mqttport)
    mqttc.loop_start()

    ser = serial.Serial(args.serialport)
    ser.timeout = 0.5

    LOG.info("Serial port %s opened with baudrate %s and parity %s", ser.name, ser.baudrate, ser.parity)

    while True:
        read_len = ser.in_waiting if ser.in_waiting > 0 else 1
        data = ser.read(read_len)

        if len(data) > 0:
            if args.dumpfile:
                dump_to_file(data)

            frames = frame_reader.read(data)
            if len(frames):
                LOG.debug("Frame count: %d", len(frames))
                for f in frames:
                    frame_received(f)
