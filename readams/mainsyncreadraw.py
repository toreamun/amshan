import datetime
import argparse
import json
import logging
import sys
import serial
import paho.mqtt.client as mqtt
from readams.meterdecode import hdlc
from readams.meterdecode import autodecoder

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=sys.stderr,
)
LOG = logging.getLogger('')


def get_arg_parser():
    parser = argparse.ArgumentParser('read HAN port')
    parser.add_argument('-v', dest='verbose', default=False)
    #    parser.add_argument('-sourceip', required=True)
    #    parser.add_argument('-mqtturl', required=True)
    return parser


decoder = autodecoder.AutoDecoder()


def new_packet(frame: hdlc.HdlcFrame):
    if frame.is_good:
        LOG.info("Got frame info content: %s", frame.information.hex())
        decoded_frame = decoder.decode_frame(frame.information)
        if decoded_frame:
            json_frame = json.dumps(decoded_frame, default=_json_converter)
            LOG.debug("Decoded frame: %s", json_frame)
            mqttc.publish("han", json_frame)
        else:
            LOG.error("Could not decode frame: %s", frame.frame_data.hex())

    else:
        LOG.warning("Got invalid frame: %s", frame.frame_data.hex())


def _json_converter(o):
    if isinstance(o, datetime.datetime):
        return o.isoformat()


def handler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    mqttc.loop_stop()
    ser.close()
    exit(0)


if __name__ == '__main__':
    args = get_arg_parser().parse_args()

    frame_reader = hdlc.HdlcOctetStuffedFrameReader(new_packet)

    mqttc = mqtt.Client()
    mqttc.enable_logger(LOG)
    mqttc.connect("192.168.1.16")
    mqttc.loop_start()

    ser = serial.Serial('/dev/ttys001')
    ser.timeout = 0.5

    LOG.info("Serial port %s opened", ser.name)

    while ser.isOpen():
        read_len = ser.in_waiting if ser.in_waiting > 0 else 1
        data = ser.read(read_len)
        if len(data) > 0:
            frame_count = frame_reader.read(data)
            if frame_count:
                LOG.debug("Frame count: %d", frame_count)
