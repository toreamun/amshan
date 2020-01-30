import argparse
import logging
import sys

import serial

from readams.meterdecode import hdlc

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


def new_packet(frame: hdlc.HdlcFrame):
    if frame.is_good:
        LOG.info("Got frame info content: %s", frame.information.hex())
    else:
        LOG.warning("Got invalid frame: %s", frame.frame_data.hex())

    if len(frame) > 267:
        LOG.warning("Hour frame!!!")


if __name__ == '__main__':
    args = get_arg_parser().parse_args()

    frame_reader = hdlc.HdlcOctetStuffedFrameReader(new_packet)

    ser = serial.Serial('/dev/ttys003')
    ser.timeout = 0.5

    LOG.info("Serial port %s opened", ser.name)

    while ser.isOpen():
        read_len = ser.in_waiting if ser.in_waiting > 0 else 1
        data = ser.read(read_len)
        if len(data) > 0:
            frame_count = frame_reader.read(data)
            if frame_count:
                LOG.debug(frame_count)
