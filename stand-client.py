#!/usr/bin/env python

import socket

PORT = 1337
HOST = 'localhost'

COM_TERMINATE = '\r\n\r\n'
COM_DELIM = '\t'

def send(str):
    #This is sort of a hack, sort of not.  I'm not sure how I want to do this yet.  Tuples
    # with auto-concat? (with DELIM in between?)
    outbuf = COM_DELIM.join(str) + COM_TERMINATE
    print 'sending',outbuf
    while (1):
        # We only really do this when we want to send, no need to loop through it every time
        try: # try TX
            sent = server.send(outbuf)
            outbuf = outbuf[sent:]
            if len(outbuf) == 0:
                break

        except socket.error: # We only want to catch SIGPIPE (server disconnect)
            pass



# create a socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0) # non-blocking

inbuf = ''
outbuf = ''

unique_ident = '033312ebed6b1e5c5a691fd6e24f7534' 
# Figure out someway to generate
# Maybe md5 of MAC address and /dev/sdX or something?
# Persistence only matters for burners, so we can use 
# pseudo-random for command/display

# connect to server
while (1):
    try:
        server.connect((HOST, PORT))
        break
    except socket.error:
        # Since non-blocking, if it doesn't work immediately, EINPROGRESS
        # Subsequent calls (while in progress) give EALREADY
        # There are other errors (actual errors), we may want to check them
        pass

while(1):

    try: #try RX
        
        if len(server.recv(1024,socket.MSG_PEEK)) == 0:
            server.close() # Bad connection, We likely want to reconnect
            continue

        # otherwise: do stuff with inbuf
        inbuf = inbuf + server.recv(1024)

    except socket.error: # Excepion (no data RX, but connection still there)
        pass
    
    # We've either got new data on inbuf, or the same data on inbuf
    # - Time to figure out what to do
    if inbuf.find(COM_TERMINATE) > -1:
        # We've got a full command
        message,inbuf = inbuf.split(COM_TERMINATE,1) # We only want one message at a time
        if message == 'IDENT':
            print 'IDENT recieved'
            send(('ID','BURN',unique_ident)) # We're a burner right now





