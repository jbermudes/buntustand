#!/usr/bin/env python
from sets import Set
import heapq
import datetime
import logging
class dumblogic:

    LOG_NAME = "logic-log"
    
    logging.basicConfig(filename=LOG_NAME,level=logging.DEBUG,)
    
    VERSION = 1

    COM_TERMINATE = '\r\n\r\n'
    COM_DELIM = '\t'

    open_on_complete = False # User configurable


    def found_new(self,conn):
        # Returns (conn,inbuf,outbuf)
        # We have a new connection, first thing to do is query it
        print "New conn.  Asking for ident"
        outbuf = 'IDENT' + self.COM_DELIM + 'V' + str(self.VERSION) + self.COM_TERMINATE
        inbuf = ''
        return (conn,inbuf,outbuf)

    def report_missing(self,(conn,inbuf,outbuf)):
        # Client has gone AWOL, assume its dead.
        # If it was burning, we need to re-add that iso (with a high priority?)
        (type,version,status,hashes,misc)= self.clients[self.conn2client[conn.fileno()]]
        if status == 'BURN': # Or any other 'active' statuses
            # If status != avail/empty/open?
            heapq.heap_push(self.burn_queue,(5,misc))
            misc = '' # We may not want to clear this (in case it reconnects?) -- Not handled yet
        stats = 'DISCONN'
        self.clients[self.conn2client[conn.fileno()]] = (type,version,status,hashes,misc)               
        del self.conn2client[conn.fileno()]
        return (conn,inbuf,outbuf)

    def assemble_message(self,parts):
        return self.COM_DELIM.join(parts) + self.COM_TERMINATE
    
    def is_hash(self,str):
        if len(str) == 32:
            for ch in str:
                if ch not in "0123456789abcdef":
                    return False
            return True
        return False

    def image_info(self,hash):
        # This is just hard-coded right now, obviously it needs to look up appropriate stuff
        # Returns a tuple of the image hash, filename, and the description.  If we want to support tabs in the description,
        # we need to modify the server code slightly (for an empty line in the description, use '\r\n \r\n')
        return ('38e3f4d0774a143bd24f1f2e42e80d63','ubuntu-8.04.1-desktop-i386.iso',"Ubuntu 8.04 (Hardy Heron) 32bit Desktop Image\r\n \r\nThis image is for the most common computers out there.  If you're in doubt, get this image.")


    def __init__(self):
        self.burn_queue = [] # Priority queue of what we want to burn format:: (priority, hash, ID)
        self.available_isos = Set() # ISO listing, along with data about ISOs
        self.conn2client = dict() # Dictionary of connection filenos to IDs (temporary)
        self.clients = dict() # Dictionary of clients and their associated data (persistent)
        self.unique_item_id = 0  # This is unique and incremented for each queue item
        
        # A client is a tuple of the following format:
        # clients[[ID]] = ([type],version,[status],(hashes),misc)
        # type: COMMAND, DISPLAY, BURNCDR, BURNDVD
        # hashes: tuple of all hashes (isos) available on that machine (returned from CAPAB)
        # misc: For burners, what's currently being burned
        # This is also what we'll expand to include statistics, etc

    def handle_communication(self,(conn,inbuf,outbuf)):
        # We know we have a completed command (\r\n\r\n) on inbuf
        logging.debug('Handle: ' + inbuf+ 'END')
        message,inbuf = inbuf.split(self.COM_TERMINATE,1)
        pieces = message.split(self.COM_DELIM) #Could be limited if we need %flow
        type = ''
        hashes = ()
        status = ''
        misc = ''
        if pieces[0] == 'ID':
            if conn.fileno() not in self.conn2client:
                self.conn2client[conn.fileno()] = pieces[3]  # UID of client
            if pieces[3] in self.clients: # Old, This doesn't actually do anything yet
                (type,version,status,hashes,misc) = self.clients[pieces[3]]

            version = pieces[1]
            type = pieces[2]
            status = 'NEW'

            self.clients[pieces[3]] = (type,version,status,hashes,misc)

            # This was only for burners, but it makes sense for everyone
            # since non-burners can push ISOs (eventually)
            outbuf = outbuf + 'CAPAB' + self.COM_TERMINATE

        elif pieces[0] == 'CAP': #reply from CAPAB
            (type,version,status,hashes,misc) = self.clients[self.conn2client[conn.fileno()]]
            hashes = pieces[1:]
            # Check if we have hashes we don't know about
            # <DUMMY CODE>
            # Right now: It's all of them
            for hash in hashes:
                outbuf = outbuf + self.assemble_message(('WHATIS',hash))
            # </DUMMY CODE>
            self.clients[self.conn2client[conn.fileno()]] = (type,version,status,hashes,misc)

        elif pieces[0] == 'STATUS': # Could be idle, could be burning
            (type,version,status,hashes,misc) = self.clients[self.conn2client[conn.fileno()]]
            if self.is_hash(pieces[1]):
                # We're burning, or done burning
                # Update our status about its status
                # If its FAIL, we need to re-queue that ISO
                if pieces[2] == 'PASS':
                    status = 'PASS'
                    if open_on_complete: # send the open command
                        outbuf = outbuf + self.assemble_message('OPEN')
                elif pieces[2] == 'FAIL':
                    status = 'FAIL'
                    heapq.heap_push(self.burn_queue,(5,misc))
                elif pieces[2] == '0':
                    status = 'BURN'
                    # Start timer
                elif pieces[2] == '100':
                    status = 'CHECKING'
                    # Get pieces[3] (== TIME) (optional?)
                    # pieces[4] has how long the client thinks it took
                    # Also record our (internal) time taken since 0
                elif pieces[2] == '25':
                    pass # These might want to be status updates
                elif pieces[2] == '50':
                    pass # If so, we need to update disconnect code to deal with
                elif pieces[2] == '75':
                    pass # more statuses (or add another field, substatus or sth)

            else: # Second argument isn't a hash
                if pieces[2] == 'OPEN':
                    # update our status about it being open
                    status = 'OPEN' # this might change
                elif pieces[2] == 'AVAIL':
                    # Tell it to burn something it has!
                    status = 'AVAIL' # this might change
                    misc = '' # When we're avail (new blank CD, we don't have an iso
                    # Remember, we're assuming everyone has all the ISOs
                    # We're also throwing away CDR vs DVD right now
                    # that'd be pieces[1], and that will get checked when we check
                    # if the machine has the capability of burning (that's a 
                    # good place to check it, when we're checking if that machine has
                    # the proper ISO (even if has a DVD iso, if it only has a CD, 
                    # it can't get sent the DVD command)
                    if len(self.burn_queue) > 0: # has elements
                        (temp_priority, temp_hash, temp_id) = heapq.heap_pop(self.burn_queue)
                        outbuf = outbuf + self.assemble_message(('BURN',temp_hash))
                        status = 'ASKED'
                        misc = temp_hash # Storing this in misc may change
                elif pieces[2] == 'EMPTY':
                    # update our status about it being empty
                    status = 'EMPTY' # this might change
                    misc = '' # When we're empty, we have no iso
            # Update our knowledge of the burner
            self.clients[self.conn2client[conn.fileno()]] = (type,version,status,hashes,misc)

        elif pieces[0] == 'ASKCAP': # Client asking for CAPAB
            outbuf = outbuf + 'CAPAB' + self.COM_TERMINATE

        elif pieces[0] == 'WHATIS':
            if self.is_hash(pieces[1]):
                outbuf = outbuf + 'INFO' + self.COM_DELIM + self.assemble_message(self.get_info(pieces[1]))
            else:
                outbuf = outbuf + 'INFO' + self.COM_DELIM + 'ENOIDEA' + self.COM_TERMINATE
                # Warn!
        
        elif pieces[0] == 'QUEUE':
            if self.is_hash(pieces[1]): # Valid Hash
                heapq.heappush(self.burn_queue,(pieces[2],pieces[1],self.unique_item_id))
                self.unique_item_id += 1
                outbuf = outbuf + 'QOK' + self.COM_TERMINATE
            else:
                # Error, Warn
                outbuf = outbuf + 'QNO' + self.COM_TERMINATE
                pass

        elif pieces[0] == 'QREPORT':
            outbuf = outbuf + 'QLIST' + self.COM_DELIM # should probably not have tab if null
            for item in sorted(self.burn_queue):
                outbuf = outbuf + self.COM_DELIM.join(reverse(item)) + self.COM_TERMINATE
                # Item is Pri, Hash, ID, we send I H P
            outbuf = outbuf + self.COM_TERMINATE # End
            if outbuf[-4:-2] != self.COM_TERMINATE: # only one \r\n (perhaps null)
                outbuf = outbuf + self.COM_TERMINATE

        elif pieces[0] == 'SREPORT':
            outbuf = outbuf + 'SLIST' + self.COM_DELIM # should probably not have tab if null
            for con in sorted(keys(self.conn2client)):
                outbuf = outbuf + self.clients[self.conn2client[con]][3] # 3 is status, already contains tab
                outbuf = outbuf + self.COM_TERMINATE
            outbuf = outbuf + self.COM_TERMINATE # End
            if outbuf[-4:-2] != self.COM_TERMINATE: # only one \r\n (perhaps null)
                outbuf = outbuf + self.COM_TERMINATE


        return (conn,inbuf,outbuf)

