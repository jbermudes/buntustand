#!/usr/bin/env python

from Queue import Queue
from sets import Set
import socket
import select  # We're polling -- Polling only works on Unix, not Windows

# Set up listening connection
HOST = ''
PORT = 1337
POLL_TIMEOUT = 100 # Wait 100 milliseconds each poll?

burn_queue = Queue(-1) # Queue to store what we want to burn
# One day this may be Priority Queue, so we'll go ahead and use data in tuple form
# CDs are queued as: (priority, 'iso-file.iso') (lower priority is better)
available_isos = Set() # ISOs 'we' have available
clients = {}

pollbooth = select.poll() # Our polling object

listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen.bind((HOST, PORT))
listen.setblocking(0) # non-blocking
listen.listen(5) # 1 + 4 waiting

while(1):
    try:
        (cl,addr) = listen.accept()
        cl.setblocking(0) # non-blocking on clients either
        print 'found: ', addr, ' == ', cl.getpeername(), ' and ', cl.fileno()
        # We need some sort of unique doohickey? A: We're using fileno()
        # I imagine these get re-used, so we need to delete after disconnect
        clients[cl.fileno()] = (cl,,'','')
        pollbooth.register(cl.fileno()) # poll for all three types (IN, PRI, OUT)
    except socket.error:
        pass # This is normal (no new connections)

    polling = pollbooth.poll(POLL_TIMEOUT)
    # This could possibly be a comprehension, but I'm not sure we want that
    for (fn,event) in polling:
        cl,inbuf,outbuf = clients[fn] # based on unique something

        # Now we use http://www.python.org/doc/2.5.2/lib/poll-objects.html
        # constants to figure out what we want to do to each.
        
        if event & select.POLLPRI: # Important data
            cl.recv(1024,socket.MSG_OOB) # get out-of-band data
            # What do we want to do with it?  Likely nothing

        if event & select.POLLIN: # data to read
        # if we have zero data here (we are flagged as having data, 
        # but actually have none, we have a dead socket, so we should
        # remove it
            print 'socket ',fn,' event: ',event
            if len(cl.recv(1024,socket.MSG_PEEK)) == 0:
                #dead socket, remove from everything
                pollbooth.unregister(cl.fileno()) #don't poll
                # We need to handle this ISO being dropped (here)
                del clients[cl.fileno()] #remove from clients
                print "dropping socket:",cl.fileno()
                continue # get out of this loop (so we don't re-set in clients)

            inbuf = inbuf + cl.recv(1024) # read data
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

#                cl,inbuf,outbuf = handle_communication((cl,inbuf,outbuf))
                pass
        
        if event & select.POLLOUT:
            #We can send whatever we need to here
            if outbuf:
                sent = cl.send(outbuf)
                outbuf = outbuf[sent-1:] # we sent 'sent' number of char, so slice outbuf accordingly

        if event & select.POLLERR:
            # Bad stuff happens?  "error" isn't well defined  What may we get?
            print "We have an error, what did you do?"
            pass
        
        if event & (select.POLLHUP | select.POLLNVAL): # Hung up or invalid (invalid shouldn't happen)
            # Go ahead and just drop it, like if disconnected
            pollbooth.unregister(cl.fileno())
            #We need to handle ISO being dropped (here)
            del clients[cl.fileno()]
            print "dropping socket:",cl.fileno()
            continue # get out of this loop (so we don't re-set in clients)
        
        
        clients[cl.fileno()] = (cl,inbuf,outbuf) # replace modified status

        
    


def queue_CD(cd, priority=10):
    """Queues a CD to be burnt.

    cd is the filename of the iso (including .iso)
    priority may be honored, lower priorities are better (default is 10)

    Returns:
    Error if CD is a bad choice
    """

    if check_valid_iso(cd):
        burn_queue.put((priority,cd))
    else:
        # Return something nasty
        pass

def get_statistics():
    # Does something fancy with printing crap to frontend
    return

def check_valid_iso(cd):
    update_isos()
    if cd in available_iso:
        return True
    else:
        return False

def update_isos():
    available_isos.clear()
    #Get a new list
    available_isos.add('ubuntu-6.06.1-alternate-i386.iso')
    available_isos.add('ubuntu-6.06.1-alternate-amd64.iso')
    available_isos.add('ubuntu-6.06.1-desktop-i386.iso')
    available_isos.add('ubuntu-8.04.1-alternate-i386.iso')
    available_isos.add('ubuntu-8.04.1-alternate-amd64.iso')
    available_isos.add('ubuntu-8.04.1-desktop-i386.iso')



