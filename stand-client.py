#!/usr/bin/env python

# This isn't much more than a dummy client to test server connections

import socket

PORT = 1337
HOST = 'localhost'

# create a socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.setblocking(0) # non-blocking

# connect to server
server.connect((HOST, PORT))

server.send('foo')

while(1):
        data = server.recv(4096) # read up to 1000000 bytes
        i += 1
        if (i < 5): # look only at the first part of the message
                print data
        if not data: # if end of data, leave loop
                break
        print 'received', len(data), 'bytes'

# close the connection
s.close()

