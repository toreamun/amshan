import fnmatch
import os
import socket
import hdlc

r2 = hdlc.HdlcOctetStuffedFrameReader()

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

#bind the socket to the port 23456, and connect
server_address = ("192.168.1.10", 3001)
sock.connect(server_address)
print ("connecting to %s" % (server_address[0]))

while True:
    b = sock.recv(1)
    frames = r2.read(b)

    for frame in frames:
        print(frame.information.hex())


# close connection
#sock.close()

