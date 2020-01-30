import argparse
import logging
import sys

import paho.mqtt.client as mqtt

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)7s: %(message)s',
    stream=sys.stderr,
)
LOG = logging.getLogger('')


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("ams/frame")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic + " " + msg.payload.hex())


if __name__ == '__main__':
    parser = argparse.ArgumentParser('ams decoder')
    parser.add_argument('-mqtthost', required=True)
    args = parser.parse_args()

    client = mqtt.Client()
    client.enable_logger(LOG)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(args.mqtthost, 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()