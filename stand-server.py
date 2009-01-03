#!/usr/bin/env python

import socket
import select  # We're polling -- Polling only works on Unix, not Windows
import dumblogic # communication handler for server

# Set up listening connection
HOST = ''
PORT = 1337
POLL_TIMEOUT = 100 # Wait 100 milliseconds each poll?

connections = {} # Keep track of connections and buffers
pollbooth = select.poll() # Our polling object
MCP = dumblogic()

listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen.bind((HOST, PORT))
listen.setblocking(0) # non-blocking
listen.listen(5) # 1 + 4 waiting

while(1):
    try:
        (conn,addr) = listen.accept()
        conn.setblocking(0) # non-blocking on connections either
        print 'found: ', addr, ' == ', conn.getpeername(), ' and ', conn.fileno()
        # We need some sort of unique doohickey? A: We're using fileno()
        # I imagine these get re-used, so we need to delete after disconnect
        connections[conn.fileno()] = (conn,'','')
        pollbooth.register(conn.fileno()) # poll for all three types (IN, PRI, OUT)
    except socket.error:
        pass # This is normal (no new connections)

    polling = pollbooth.poll(POLL_TIMEOUT)
    # This could possibly be a comprehension, but I'm not sure we want that
    for (fn,event) in polling: # from polling, we get fileno and event mask
        conn,inbuf,outbuf = connections[fn] # based on fileno

        # Now we use http://www.python.org/doc/2.5.2/lib/poll-objects.html
        # constants to figure out what we want to do to each.
        
        if event & select.POLLPRI: # Important data
            conn.recv(1024,socket.MSG_OOB) # get out-of-band data
            # What do we want to do with it?  Likely nothing

        if event & select.POLLIN: # data to read
        # if we have zero data here (we are flagged as having data, 
        # but actually have none, we have a dead socket, so we should
        # remove it
            print 'socket ',fn,' event: ',event
            if len(conn.recv(1024,socket.MSG_PEEK)) == 0:
                #dead socket, remove from everything
                pollbooth.unregister(conn.fileno()) #don't poll
                # We need to handle this ISO being dropped (here)
                MCP.report_missing((conn,inbuf,outbuf))
                del connections[conn.fileno()] #remove from connections
                print "dropping socket:",conn.fileno()
                conn.close()
                continue # get out of this loop (so we don't re-set in connections)

            inbuf = inbuf + conn.recv(1024) # read data
            print "read: ",len(inbuf)," buf: ",inbuf
            #if we don't get it all here, we'll have another poll immediately
            #afterwards where we'll get the rest
            if inbuf.find('\r\n\r\n'): # end of a command so deal with it
                # We need to deal with it some how.  Likely in a separate area
                # This separate area will figure out what to reply with, which 
                # includes figuring out what iso to hand over
                # It very well may be that iso and status are completely contained
                # in this other module, along with lots of other record keeping goodies
                # If that's the case, we don't need them here (really, they make more 
                # sense in another location.  We can rename clients to connections 
                # and only deal with cl and the two buffers, like proper separation
                # dictates we ought to.
                # -- I've convinced myself.  So, whatever we pass this to should modify
                # the buffers appropriately (please be sure to append/slice, and not 
                # simply set/delete), and this will magically take care of TX/RX without
                # a care for what it's sending/recieving
                #   I imagine this will be some other module with proper public methods
                # (well, what... two public methods? handle_stuff() and socket_disconnect() 
                # All of the logic lives inside of it, including which sockets are 
                # burners, which are clients and it also will get the stuff from 
                # the clients to queue and stuff.  In otherwords, ignore *all* 
                # of the functions below because they belong in magic-smart-module
                conn,inbuf,outbuf = MCP.handle_communication((conn,inbuf,outbuf))
                pass
        
        if event & select.POLLOUT:
            #We can send whatever we need to here
            if outbuf:
                sent = conn.send(outbuf)
                outbuf = outbuf[sent:] # we sent 'sent' number of char, so slice outbuf accordingly

        if event & select.POLLERR:
            # Bad stuff happens?  "error" isn't well defined  What may we get?
            print "We have an error, what did you do?"
            pass
        
        if event & (select.POLLHUP | select.POLLNVAL): # Hung up or invalid (invalid shouldn't happen)
            # Go ahead and just drop it, like if disconnected
            pollbooth.unregister(conn.fileno())
            #We need to handle ISO being dropped (here)
            MCP.report_missing((conn,inbuf,outbuf))
            del connections[conn.fileno()]
            print "dropping socket:",conn.fileno()
            conn.close()
            continue # get out of this loop (so we don't re-set in connections)
        
        
        connections[conn.fileno()] = (conn,inbuf,outbuf) # replace modified status


