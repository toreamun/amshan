import socket
import hdlc

# create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the socket to the port 23456, and connect
server_address = ("192.168.1.10", 3001)
sock.connect(server_address)
print ("connecting to %s" % (server_address[0]))

r2 = hdlc.HdlcOctetStuffedFrameReader()

while True:
    b = sock.recv(10)
    r2.read(b)


# close connection
sock.close()

