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
        # We need some sort of unique doohickey.  We're using fileno()
        # I imagine these get re-used, so we need to delete after disconnect
        #clients.append((cl,'','','')) # connect, ISO, status, buffer
        clients[cl.fileno()] = (cl,'','','')
        pollbooth.register(cl.fileno()) # poll for all three types (IN, PRI, OUT)
    except socket.error:
        pass # This is normal (no new connections)

    polling = pollbooth.poll(POLL_TIMEOUT)
    # This could possibly be a comprehension, but I'm not sure we want that
    for (fn,event) in polling:
        cl,iso,status,buf = clients[fn] # based on unique something

        # Now we use http://www.python.org/doc/2.5.2/lib/poll-objects.html
        # constants to figure out what we want to do to each.
        
        if event & (select.POLLIN | select.POLLPRI): # data to read
            # This *may* be how we want to deal with it, it may not.
            buf = buf + cl.recv(4096)
            if buf.find('\r\n\r\n'): # end of a command so deal with it
                cl,iso,status,buf = handle_communication((cl,iso,status,buf))
            clients[cl.fileno()] = (cl,iso,status,buf) # replace modified status
        
    


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



