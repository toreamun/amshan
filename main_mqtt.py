import argparse
import datetime
import json
import logging
import signal
import sys
import time

import paho.mqtt.client as mqtt
import serial

from smartmeterdecode import autodecoder, hdlc

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


def signal_handler(signal_number, stack_frame):
    LOG.info(
        "%s signal received. Exiting gracefully.", signal.Signals(signal_number).name
    )
    close_resources()
    exit(0)


def close_resources():
    if ser is not None and ser.isOpen():
        LOG.debug("Close serial port %s", ser.name)
        ser.close()
    if logfile is not None and logfile:
        LOG.debug("Close frame logfile %s", logfile.name)
        logfile.close()
    if mqtt_client is not None:
        LOG.debug("Close MQTT client")
        mqtt_client.loop_stop()


def dump_to_file(dump_data: bytes):
    for b in dump_data:
        is_flag = b == b"\x7e"[0]
        if is_flag:
            logfile.write("\n")
        logfile.write("{:02x}".format(b))
        if is_flag:
            logfile.write("\n")


def hdlc_frame_received(frame: hdlc.HdlcFrame):
    if frame.is_good_ffc and frame.is_expected_length:
        LOG.debug("Got frame info content: %s", frame.information.hex())
        decoded_frame = decoder.decode_frame_content(frame.information)
        if decoded_frame:
            json_frame = json.dumps(decoded_frame, default=json_converter)
            LOG.debug("Decoded frame: %s", json_frame)
            mqtt_client.publish(args.mqtttopic, json_frame)
        else:
            LOG.error("Could not decode frame: %s", frame.frame_data.hex())
    else:
        LOG.warning("Got invalid frame: %s", frame.frame_data.hex())


if __name__ == "__main__":

    args = get_arg_parser().parse_args()

    ser = None
    mqtt_client = None
    logfile = None

    signal.signal(signal.SIGINT, signal_handler)

    try:
        if args.dumpfile:
            logfile = open(args.dumpfile, "w+")

        decoder = autodecoder.AutoDecoder()
        frame_reader = hdlc.HdlcFrameReader(False)

        mqtt_client = mqtt.Client()
        mqtt_client.enable_logger(LOG)
        try:
            mqtt_client.connect(args.mqtthost, port=args.mqttport)
        except Exception as ex:
            LOG.error(
                "Could connect to MQTT host %s on port %s: %s",
                args.mqtthost,
                args.mqttport,
                ex,
            )
            raise
        mqtt_client.loop_start()

        LOG.info("MQTT client connected to %s on port %s", args.mqtthost, args.mqttport)

        ser = serial.Serial()
        ser.port = args.serialport
        if args.ser_parity:
            ser.parity = args.ser_parity
        if args.ser_baudrate:
            ser.baudrate = args.ser_baudrate
        ser.timeout = 0.5
        try:
            ser.open()
        except serial.SerialException as ex:
            LOG.error("Could not open serial: %s", ex.strerror)
            raise

        LOG.info(
            "Serial port %s opened with baudrate %s and parity %s",
            ser.name,
            ser.baudrate,
            ser.parity,
        )

        while True:
            try:
                if not ser.isOpen():
                    ser.open()
                read_len = ser.in_waiting if ser.in_waiting > 0 else 1
                data = ser.read(read_len)
            except serial.SerialException as ex:
                LOG.error("Trouble reading from serial port: %s", ex)
                data = []
                ser.close()
                time.sleep(2)

            if len(data) > 0:
                if args.dumpfile:
                    dump_to_file(data)

                frames = frame_reader.read(data)
                if len(frames):
                    for f in frames:
                        hdlc_frame_received(f)
    except Exception as ex:
        LOG.error("Exception: %s", ex)
        close_resources()
