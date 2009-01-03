#!/usr/bin/env python
from sets import Set
class dumblogic:

    COM_TERMINATE = '\r\n\r\n'
    COM_DELIM = '\t'

    def __init__(self):
        burn_queue = [] # heapq
        available_isos = Set() # No prior knowledge of ISOs
        clients = {} # Collection of clients and their associated data
        
        # A client is a tuple of the following format:
        # 

    def handle_communication(self,(client,inbuf,outbuf)):
        # We know we have a completed command (\r\n\r\n) on inbuf
        
        return (client,inbuf,outbuf)
    
    def found_new(self,client):
        # Returns (client,inbuf,outbuf)
        # We have a new connection, first thing to do is query it
        print "New conn.  Asking for ident"
        outbuf = 'IDENT' + self.COM_TERMINATE
        inbuf = ''
        return (client,inbuf,outbuf)

    def report_missing(self,(client,inbuf,outbuf)):
        # Client has gone AWOL, assume its dead.
        return (client,inbuf,outbuf)


