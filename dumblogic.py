#!/usr/bin/env python
from sets import Set
class dumblogic:

# Protocol pieces:
# x -- Fully supported
# * -- protocol support (maybe not functional)
# <- IDENT *
# -> ID *
# <- CAPAB *
# -> CAP *
# -> STATUS AVAIL|BUSY
# <- BURN [HASH]
# -> STATUS [HASH] 0
# -> STATUS [HASH] %
# -> STATUS [HASH] 100
# -> STATUS [HASH] PASS|FAIL
# <- OPEN
# -> STATUS OPEN
# <- WHATIS
# -> INFO HASH FILE DESC

    VERSION = 1

    COM_TERMINATE = '\r\n\r\n'
    COM_DELIM = '\t'

    def __init__(self):
        self.burn_queue = [] # Priority queue of what we want to burn
        self.available_isos = Set() # ISO listing, along with data about ISOs
        self.conn2client = dict() # Dictionary of connection filenos to IDs (temporary)
        self.clients = dict() # Dictionary of clients and their associated data (persistent)
        
        # A client is a tuple of the following format:
        # clients[[ID]] = ([type],version,[status],(hashes),misc)
        # type: COMMAND, DISPLAY, BURNCDR, BURNDVD
        # hashes: tuple of all hashes (isos) available on that machine (returned from CAPAB)
        # misc: For burners, what's currently being burned
        # This is also what we'll expand to include statistics, etc

    def handle_communication(self,(conn,inbuf,outbuf)):
        # We know we have a completed command (\r\n\r\n) on inbuf
        message,inbuf = inbuf.split(self.COM_TERMINATE,1)
        pieces = message.split(self.COM_DELIM) #Could be limited if we need %flow
        type = ''
        hashes = ()
        status = ''
        misc = ''
        if pieces[0] == 'ID':
            if conn.fileno() not in self.conn2client:
                self.conn2client[conn.fileno()] = pieces[3]
            if pieces[3] in self.clients: # Old, This doesn't actually do anything yet
                (type,version,status,hashes,misc) = self.clients[pieces[3]]

            version = pieces[1]
            type = pieces[2]
            status = 'NEW'

            self.clients[pieces[3]] = (type,version,status,hashes,misc)

            # This was only for burners, but it makes sense for everyone
            # since non-burners can push ISOs (eventually)
            outbuf = outbuf + 'CAPAB' + self.COM_TERMINATE

        if pieces[0] == 'CAP': #reply from CAPAB
            (type,version,status,hashes,misc) = self.clients[self.conn2client[conn.fileno()]]
            hashes = pieces[1:]
            # Check if we have hashes we don't know about
            # <DUMMY CODE>
            # Right now: It's all of them
            for hash in hashes
                outbuf = outbuf + assemble_message('WHATIS',hash)
            # </DUMMY CODE>
            self.clients[self.conn2client[conn.fileno()]] = (type,version,status,hashes,misc)

        if pieces[0] == 'STATUS': # Could be idle, could be burning
            if is_hash(pieces[1]):
                # We're burning, or done burning (not idle)
            else
                if pieces[1] == 'OPEN':
                elif pieces[1] == 'AVAIL':
                elif pieces[1] == 'EMPTY':
                




        return (conn,inbuf,outbuf)
    
    def found_new(self,conn):
        # Returns (conn,inbuf,outbuf)
        # We have a new connection, first thing to do is query it
        print "New conn.  Asking for ident"
        outbuf = 'IDENT' + self.COM_DELIM + 'V' + str(self.VERSION) + self.COM_TERMINATE
        inbuf = ''
        return (conn,inbuf,outbuf)

    def report_missing(self,(conn,inbuf,outbuf)):
        # Client has gone AWOL, assume its dead.
        del self.conn2client[conn.fileno()]
        return (conn,inbuf,outbuf)

    def assemble_message(self,parts)
        return self.COM_DELIM.join(parts) + self.COM_TERMINATE
    
    def is_hash(str)
        if len(str) > 10: # This can be done better, obviously
            return True
        return False

