#!/usr/bin/env python
from Queue import Queue
from sets import Set
class dumblogic:
#   burn_queue = Queue(-1) # Queue to store what we want to burn
    # One day this may be Priority Queue, so we'll go ahead and use data in tuple form
    # CDs are queued as: (priority, 'iso-file.iso') (lower priority is better)
#   available_isos = Set() # ISOs 'we' have available
    
    def __init__(self):
        burn_queue = Queue(-1) # Unlimited Queue
        available_isos = Set() # No prior knowledge of ISOs
        clients = {}

    def handle_communication(self,(client,inbuf,outbuf)):
        # We know we have a completed command (\r\n\r\n) on inbuf
        return (client,inbuf,outbuf)

    def report_missing(self,(client,inbuf,outbuf)):
        pass

