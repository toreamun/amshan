import fnmatch
import os
import socket
import hdlc
import decode
import json
import asyncio

reader = hdlc.HdlcOctetStuffedFrameReader()

#folder = "/Users/tore/Downloads/han-port-1.15"
# listOfFiles = os.listdir(folder)
# pattern = "*.dat"
# for entry in listOfFiles:
#     if fnmatch.fnmatch(entry, pattern):
#         print("####################################")
#         print(entry)
#
#         filepath = os.path.join(folder, entry)

# filepath = "/Users/tore/Downloads/HAN/ikke/han-data-4572.dat"
# with open(filepath, "rb") as f:
#     byte = f.read(1)
#     while byte != b"":
#         # Do stuff with byte.
#         r2.read(byte)
#         byte = f.read(1)


# create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#bind the socket to the port 3001, and connect
server_address = ("192.168.1.10", 3001)
sock.connect(server_address)
print ("connecting to %s" % (server_address[0]))

while True:
    bytes = sock.recv(1)
    frames = reader.read(bytes)

    for frame in frames:
        msg = decode.LlcPdu.parse(frame.information)
        #msg = decode.decode_frame(frame._complete_buffer)

        #print(json.dumps(msg))

        print(msg)
        print(f"{msg.meter_data.meter_ts}: {msg.meter_data.data.pwr_act_pos} W")
        try:
            print(f"Current: {msg.data.IL1} A")
            print(f"Voltage: {msg.data.ULN1} V")
            print(f"Reactive: {msg.data.pwr_react_neg} VAr")
        except AttributeError:
            pass

# close connection
sock.close()

