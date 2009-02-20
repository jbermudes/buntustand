#!/usr/bin/env python

import socket
import datetime

from pywodim import *

PORT = 1337
HOST = 'localhost'

VERSION = 1

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

def get_hashes():
    # Obviously this is a stub
    # Returns a tuple of hashes
    return ('38e3f4d0774a143bd24f1f2e42e80d63','bbd21ded02c06b41c59485266833937a','b78ef719e3361e726b89bab78c526ad0','c69e34e92d5402d1b87e6babc739f774')

def drive_type():
    # Returns the type of the drive (assumed that DVD drives can burn CDs)
    return 'CDR'

def disc_type():
    # Returns the type (CDR or DVD) of the disc in the drive
    return 'CDR'

def image_info(hash):
    # This is just hard-coded right now, obviously it needs to look up appropriate stuff
    # Returns a tuple of the image hash, filename, and the description.  If we want to support tabs in the description,
    # we need to modify the server code slightly (for an empty line in the description, use '\r\n \r\n')
    return ('38e3f4d0774a143bd24f1f2e42e80d63','ubuntu-8.04.1-desktop-i386.iso',"Ubuntu 8.04 (Hardy Heron) 32bit Desktop Image\r\n \r\nThis image is for the most common computers out there.  If you're in doubt, get this image.")

# Pywodim
def tray_open(): # Opens the Tray
    openTray()

# Pywodim
def tray_close(): # Opens the Tray
    closeTray()

# Pywodim
def start_burn(file): # Starts burning (filename)
    burn(file, isRealBurn=True)

# Pywodim
def tray_status(): # returns status of the tray (open, empty, full)
    device = getDefaultDevice()
    if (isTrayOpen(device)):
	    return 'open'
    else:
	return 'full' # empty and full imply closed

def burn_status(): # Returns a number (percentage) of our progress through the burn
    return 26

def get_filename(hash): # Returns a filename (from an image directory? absolute path?) for the given hash
    return 'ubuntu-8.04.1-1-desktop-i386.iso'

def check_md5():
    #checks md5 of the disk in the drive
    return 1

# create a socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0) # non-blocking

inbuf = ''
outbuf = ''

burning = '' # hash of current CD we're burning

marker = datetime.datetime.now()

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
        pieces = message.split(COM_DELIM)
        if pieces[0] == 'IDENT':
            print 'RX: IDENT, V',pieces[1]
            send(('ID','V' + str(VERSION),'BURN'+ drive_type(),unique_ident)) # We're a CD burner right now
        if pieces[0] == 'CAPAB':
            print 'RX: CAPAB'
            send(('CAP','BURN' + drive_type(),COM_DELIM.join(get_hashes()))) # We could re-split hashes; that's silly
            marker = datetime.datetime.now() # We'll send our first STATUS AVAIL|EMPTY in 10 seconds
        if pieces[0] == 'WHATIS':
            send(('INFO',COM_DELIM.join(image_info(pieces[1])))) # We could re-split info, but its not required
        if pieces[0] == 'OPEN':
            # Open the tray
            open_tray()
            # (sending stuff will happen as a response to the tray opening)
            pass
        if pieces[0] == 'BURN':
            if pieces[1] not in get_hashes():
                # Error
                send(('ERROR','NOISO','Burner does not have this ISO.'))
                pass
            else:
                # Start Burn
                burning = pieces[1]
                start_burn(get_filename(pieces[1]))
                send(('STATUS',pieces[1],'0')) # Burn starts at 0
                marker = datetime.datetime.now() # For timing purposes

    # That's everything that the server will send us (except for file transfer stuff)
    # Everything else is generated based on stuff happening locally
    # These are all mutually exclusive; could use elif
    if tray_status() == 'open':
        send(('STATUS',drive_type(),'OPEN'))
    elif burn_status() == 100:
        timediff = datetime.datetime.now() - marker
        send(('STATUS',burning,'100','TIME',str(timediff.days*3600*24 + timediff.seconds))) # I hope not days 
        if check_md5():
            send(('STATUS',burning,'PASS'))
        else:
            send(('STATUS',burning,'FAIL'))
        # Either way, make sure its unmounted (md5 might already do this?)
        # We likely need to unmount before md5 check too?
    elif burn_status() % 25 == 0: # This is a little awkward, could theoretically send 26 or whatnot
        # effectively disabled for now (always returns 26 % 25 = 1 != 0)
        send(('STATUS',burning,get_burn_status)) # we also only want to do this once per milestone
    else:
        timediff = datetime.datetime.now() - marker
        if (timediff.days > 0 or timediff.seconds >= 10):
            # I would hope we wouldn't be waiting a full day
            marker = datetime.datetime.now()
            if tray_status() == 'empty':
                send(('STATUS',drive_type(),'EMPTY'))
            elif tray_status() == 'full':
                send(('STATUS',disc_type(),'AVAIL'))



