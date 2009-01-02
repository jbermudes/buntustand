#!/usr/bin/env python

# This isn't much more than a dummy client to test server connections

import socket

PORT = 1337
HOST = 'localhost'

# create a socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0) # non-blocking

inbuf = ''
outbuf = ''

# connect to server
server.connect((HOST, PORT))

while(1):

    try: #try RX
        inbuf = server.recv(1024)

        if len(inbuf) == 0:
            server.close() # Bad connection, We likely want to reconnect
            continue

        # do stuff with buf


    except socket.error: # Excepion (no data RX, but connection still there)
        pass

    try: # try TX
        sent = server.send(outbuf)
        outbuf = outbuf[sent:]

    except socket.error: # We only want to catch SIGPIPE (server disconnect)
        pass

