#!/usr/bin/env python

import curses
import curses.wrapper
import curses.panel
import curses.ascii
import time

import socket

import ubuntudisc
from ubuntudisc import DiscPackage
from ubuntudisc import UbuntuDisc

#import logging
#LOG_NAME = "command-log"
#logging.basicConfig(filename=LOG_NAME,level=logging.DEBUG,)

PORT = 1337
HOST = 'localhost'

VERSION = 1

COM_TERMINATE = '\r\n\r\n'
COM_DELIM = '\t'

COLOR_U = 1
COLOR_K = 2
COLOR_E = 3
COLOR_X = 4
COLOR_PASS = 5
COLOR_FAIL = 6

KEY_UP = 0
KEY_DOWN = 1
KEY_LEFT = 2
KEY_RIGHT = 3
KEY_CONFIRM = 4
KEY_CANCEL = 5
KEY_EJECT = 6
KEY_RENAME = 7
KEY_DELETE = 8
KEY_PLUS = 9
KEY_MINUS = 10
KEY_INSERT = 11
KEY_EDIT = 12

keysdown = []
blankkeys = [0,0,0,0,0,0,0,0,0,0,0,0,0]

KEYCODE_UP = 'h'
KEYCODE_DOWN = 'l'
KEYCODE_LEFT = 'j'
KEYCODE_RIGHT = 'k'
KEYCODE_CONFIRM = 'ENTER'
KEYCODE_CANCEL = 'CANCEL'
KEYCODE_EJECT = 'e'
KEYCODE_RENAME = 'r'
KEYCODE_INSERT = 'i'
KEYCODE_EDIT = 'e'
KEYCODE_DELETE = 'd'

frame_count = 0
target_time = 0

order_cursor = 0
order_mode = 0
order_spinner_indices = [0,0,0,0,0,0]
selected_pkg = 0
alert_text = ""

packages_cursor = 0

clients_cursor = 0
clients_mode = 0
num_clients = 6

queue_cursor = 0
queue_mode = 0

packages = [DiscPackage("Custom CD", None), 
            DiscPackage("1 Intrepid Desktop i386", [UbuntuDisc(ubuntudisc.UBUNTU, ubuntudisc.V_8_10, ubuntudisc.DESKTOP, ubuntudisc.I386)]),
            DiscPackage("2 Hardy Ubuntu Desk. i386", [UbuntuDisc(ubuntudisc.UBUNTU, ubuntudisc.V_8_04_2, ubuntudisc.DESKTOP, ubuntudisc.I386), UbuntuDisc(ubuntudisc.UBUNTU, ubuntudisc.V_8_04_2, ubuntudisc.DESKTOP, ubuntudisc.I386)]),
           ]
package_names = []


quantities = range(1, 64)

num_flavors = len(ubuntudisc.FLAVOR_NAMES)
num_versions = len(ubuntudisc.VERSION_NAMES)
num_architectures = len(ubuntudisc.ARCHITECTURE_NAMES)
num_editions = len(ubuntudisc.EDITION_NAMES)

active_tab = 0
is_running = True
tabnames = ("Order","Packages","Clients","Queue","")
tabs = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0) # non-blocking

client_names = ["JESS", "FLANNEL", "NHAINES", "YASUMOTO", "LIKETOTA", ""]
client_ip = ["X.X.128.87", "X.X.128.92", "X.X.128.33", "X.X.128.103", "X.X.128.79", ""]
client_jobs = ["Ubuntu 8.10 i386 Dsk.", "Kubuntu 8.10 i386 Dsk.", "Edubuntu 8.10 i386 Srv.", "", "Ubuntu 8.10 i386 Alt.", ""]
client_status = ["BURNING (87%)", "TEST PASSED", "VERIFYING", "AWAITING MEDIA", "BURNING (8%)", "NO CLIENT"]
    

# clients are a tuple of (ID,Name,type,status). status is hash+DELIM+msg
#('033312ebed6b1e5c5a691fd6e24f7532','Client0','CDR','1231231231231231231234\t0')
clients = [('033312ebed6b1e5c5a691fd6e24f7532','Client0','CDR','ea6d44667ea3fd435954d6e1f0e89122\t50'),
           ('033312ebed6b1e5c5a691fd6e24f7533','Client1','CDR','ea6d44667ea3fd435954d6e1f0e89122\tPASS'),
           ('033312ebed6b1e5c5a691fd6e24f7534','Client2','CDR','ea6d44667ea3fd435954d6e1f0e89122\tFAIL')
            ]

# Queue items are tuples of id,hash,priority
queue = [(0, "ea6d44667ea3fd435954d6e1f0e89122", 50),
         (1, "ea6d44667ea3fd435954d6e1f0e89122", 23),
         (2, "ea6d44667ea3fd435954d6e1f0e89122", 75)
        ]



inbuf = ''
outbuf = ''

#######################################
## Socket Functions
#######################################

def get_ident(): # Return our client ID
    # Figure out someway to generate
    # Maybe md5 of MAC address and /dev/sdX or something?
    # Persistence only matters for burners, so we can use 
   # pseudo-random for command/display
    return '033312ebed6b1e5c5a691fd6e24f7535'


########################################
## Burner logic
########################################

def get_job_and_status(index):
    client = clients[index]
    
    hsh,status = client[3].split(COM_DELIM) # hash,status
    tup = ubuntudisc.hash2Tuple(hsh)
    job = ubuntudisc.tuple2String(tup)
    
    return job, status

def rename_client(i, name):
    clients[i] = (clients[i][0], name, clients[i][2], clients[i][3])

##########################################
## CD info stuff
##########################################
def get_hash_info(hash): # Dummy
    info = [('Ubuntu','8.04.1','AMD64','Desktop'),('Kubuntu','8.10','i386','Alternate'),
            ('Xubuntu','6.06.2','i386','Server'),('Edubuntu','8.04.1','AMD64','Alternate')]
    index = int(hash,16) % len(info)
    return info[index]

def is_hash(str):
    if len(str) == 32:
        for ch in str:
            if ch not in "0123456789abcdef":
                return False
        return True
    return False


def add_cd(distro, version, arch, typ):
    available

#####################################
## Client Commands to Server
#####################################

# id shouldnt be 0 cause that's a custom CD
def submit_package_order(pkg_id):

    pkg = packages[pkg_id]
    
    discs = pkg.contents
    
    for disc in discs:
        submit_order(disc.flavor, disc.version, disc.architecture, disc.edition, 1, 50)

def submit_order(f, v, a, e, q, p):
    if (f,v,e,a) not in ubuntudisc.HASHES:
        return False
        
    disc = UbuntuDisc(f,v,e,a)
    hashcode = disc.hash
    return True

def eject_client(id):
    eject = 1

#####################################
## Packages stuff
#####################################

def add_package(name):
    global packages
    
    packages.append(name)
    
def delete_package(i):
    global packages
    
    if i > 0:
        del packages[i]
    else:
        curses.flash()

def update_package_names():
    global package_names
    
    package_names = []
    
    for pkg in packages:
        package_names.append(pkg.name)
########################################
## Queue stuff
########################################

def get_printable_queue():
    printable = []
    for item in queue:
        printable.append( ubuntudisc.tuple2String(ubuntudisc.hash2Tuple(item[1])) + " " + str(item[2]) )
    
    return printable

def delete_from_queue(i):
    if len(queue) > 0:
        del queue[i]

#################################################
## Curses Functions
#################################################

def get_console_string(scr, msg="? ", row=1, col=1, maxlen=0):
    curses.echo()
    
    scr.addstr(row, col, msg)
    offset = len(msg)
    if maxlen > 0:
        scr.addstr(row, col+offset, "_"*maxlen)
    string = scr.getstr(row, col+offset)
    curses.noecho()
    
    if maxlen > 0:
        string = string[0:maxlen]
    
    return string

def make_box(scr,y,x,h,w,attr=0): # y,x is top left corner (of border), h,w is empty space inside
    for i in range(y+1,y+h+1):
        scr.addch(i,x,curses.ACS_VLINE | attr)
        scr.addch(i,x+w+1,curses.ACS_VLINE | attr)

    for i in range(x+1,x+w+1):
        scr.addch(y,i,curses.ACS_HLINE | attr)
        scr.addch(y+h+1,i,curses.ACS_HLINE | attr)

    scr.addch(y,x,curses.ACS_ULCORNER | attr)
    scr.addch(y,x+w+1,curses.ACS_URCORNER | attr)
    scr.addch(y+h+1,x,curses.ACS_LLCORNER | attr)
    scr.addch(y+h+1,x+w+1,curses.ACS_LRCORNER | attr)

def make_ugly_box(scr,y,x,h,w,attr=0): # y,x is top left corner (of border), h,w is empty space inside
    #for i in range(y+1,y+h+1):
        #scr.addch(i,x,'|', attr)
        #scr.addch(i,x+w+1, '|', attr)

    for i in range(x+1,x+w+1):
        scr.addch(y,i,'=', attr)
        scr.addch(y+h+1,i,'=', attr)

    #scr.addch(y,x,'/', attr)
    #scr.addch(y,x+w+1,'\\', attr)
    #scr.addch(y+h+1,x,'\\', attr)
    #scr.addch(y+h+1,x+w+1,'/', attr)

def draw_tabs(scr,names,active):
    for i in range(0,65):
        scr.addch(1,i,curses.ACS_S1)
    for i in range(0,len(names)):
        #att = curses.A_DIM
        att = 0
        if (i != active):
            att |= curses.A_REVERSE
#       scr.addstr(0, i*13, " ", curses.A_REVERSE)
        scr.addstr(0, i*13, " /          \\", att | curses.A_REVERSE)
        scr.addnstr(0, i*13+2, ' ' + tabnames[i] + '         ',10,att)
    scr.addstr(1,active*13+2,"          ")

def draw_spinner(scr, y, x, label, value, selected, label_tab=10, value_tab=10):
    
    attr = 0
    if selected == True:
        attr = curses.A_REVERSE
    scr.addstr(y,x," "*(label_tab+value_tab), attr)
    scr.addstr(y, x, label, attr)
    scr.addstr(y, x+label_tab, "[", attr)
    scr.addstr(y, x+label_tab+1, value, attr)
    scr.addstr(y, x+label_tab+value_tab, "]", attr)

def draw_button(scr, y, x, label, selected):
    attr = 0
    if selected == True:
        attr = curses.A_REVERSE
    
    scr.addstr(y, x, " " * (len(label)+3), attr)
    scr.addstr(y, x, "[", attr)
    scr.addstr(y, x+2, label, attr)
    scr.addstr(y, x+3+len(label), "]", attr)

def draw_scrollpane(scr, y, x, h, w, title, data, sel_index):
    start_row = 0
    if sel_index > h - 1:
        start_row = sel_index - h + 1
        
    end_row = start_row + h
    if end_row > len(data):
        end_row = len(data)
    
    attr = 0
    make_ugly_box(scr, y, x, h, w)
    scr.addstr(y, (x + w) / 2 - len(title) / 2, " " + title + " ")
    for row in range(start_row, end_row):
        i = row % len(data)
        if i == sel_index:
            attr = curses.A_REVERSE
        else:
            attr = 0
            
        scr.addstr(y + (row - start_row) +1, x+1, " " * (w-1), attr)
        scr.addstr(y + (row - start_row) +1, x+1, str(i) + ". " + data[i], attr)
    
    # arrows
    if start_row > 0:
        scr.addch(y+1, x+w, curses.ACS_UARROW)
    
    if end_row < len(data):
        scr.addch(y+h, x+w, curses.ACS_DARROW)

## ****************************************
## Tab Draw Functions
## ****************************************

# The Orders Tab
def draw_menu_order(scr):
    
    scr.erase()
    y_max,x_max = scr.getmaxyx()
    pkg_id = 0
    if order_mode == 0:
        pkg_id = order_cursor
    else:
        pkg_id = selected_pkg
    draw_scrollpane(scr, 2, 1, 5, 60, "CD Packages", package_names, pkg_id)

    # Single CD stuff
    indent = 9
    row = 10
    
    
    if order_mode == 1 or (order_mode == 2 and selected_pkg == 0) or (order_mode == 3 and selected_pkg == 0):
        scr.addstr(9,x_max/2-7," Single CD")

        m = order_mode == 1        

        # Flavor
        draw_spinner(scr, row, indent, "Flavor:", ubuntudisc.FLAVOR_NAMES[order_spinner_indices[0] % num_flavors], (m and order_cursor == 0))
        #scr.addstr(3,indent+11,"E",curses.color_pair(COLOR_E))
        
        # Version
        draw_spinner(scr, row+1, indent, "Version:", ubuntudisc.VERSION_NAMES[order_spinner_indices[1] % num_versions], (m and order_cursor == 1))
        
        # Architecture
        draw_spinner(scr, row+2, indent, "Arch:", ubuntudisc.ARCHITECTURE_NAMES[order_spinner_indices[2] % num_architectures], (m and order_cursor == 2))
        
        # Type
        draw_spinner(scr, row+3, indent, "Edition:", ubuntudisc.EDITION_NAMES[order_spinner_indices[3] % num_editions], (m and order_cursor == 3))
        
        # Quantity
        #draw_spinner(scr, row, indent+27, "Quantity:", str(quantities[order_spinner_indices[4] % len(quantities)]), (m and order_cursor == 4), 11, 5)
        
        # Priority
        #draw_spinner(scr, row+1, indent+27, "Priority:", "1", (m and order_cursor == 5), 11, 5)

    # Submits, Clear
    draw_button(scr, y_max-2, 10, "Reset", (order_mode == 2 and order_cursor % 2 == 0))
    draw_button(scr, y_max-2, 35, "Submit Order", (order_mode == 2 and order_cursor % 2 == 1))
    
    scr.addstr(14, 4, str(order_cursor))
    
    if len(alert_text) > 0:
        scr.addstr(y_max-1, 1, (" " * (x_max-3)), curses.A_REVERSE)
        scr.addstr(y_max-1, 1, alert_text, curses.A_REVERSE)

# The Packages Tab
def draw_menu_packages(scr):
    scr.erase()
    y_max,x_max = scr.getmaxyx()
    
    selection = packages_cursor % len(packages)
    
    draw_scrollpane(scr, 2, 1, 10, 60, "CD Packages", package_names, selection)
    
    scr.addstr(16, 2, "[I]nsert New     [E]dit     [D]elete")

# The Clients Tab
def draw_menu_clients(scr):
    scr.erase()
    selected_client = clients_cursor % len(clients)
    
    y_max,x_max = scr.getmaxyx()
    width = 32
    height = 4
    
    # clients are a tuple of (ID,Name,type,status). status is hash+DELIM+msg
    for i in range(len(clients)):
        cl = clients[i]
        row = i / 2
        col = 0 if i % 2 == 0 else 1
        posy = (row * height)+2
        posx = (col * width)
        job,status = get_job_and_status(i) # hash,status
        
        attr = curses.color_pair(COLOR_X) | curses.A_BOLD if i == selected_client else 0
        make_ugly_box(tabs[2],posy,posx,2,30, attr)
        scr.addstr(posy, posx+2, cl[1], attr) # name
        #scr.addstr(posy, posx+15, cl[0], attr) # ID...IP?
        scr.addstr(posy+1, posx+1, "Job: " + job)
        scr.addstr(posy+2, posx+1, "Status: " + status)
    
    #scr.addstr(14,3,"Rename: ")
    
    scr.addstr(y_max-1,2,"J/K: Up/Down     E: Eject     R: Rename")

def draw_menu_queue(scr, update=0):
    scr.erase()
    
    queue_len = len(queue)
    
    if queue_len > 0:
        selected_item = queue_cursor % queue_len
    else:
        selected_item = 0
    
    y_max,x_max = scr.getmaxyx()
    offset = 2
    draw_scrollpane(scr, 2, 1, 10, 60, "", get_printable_queue(), selected_item)
    scr.addstr(2,2,"# ")
    scr.addstr(2,6," Distro ")
    scr.addstr(2,18," Ver. ")
    scr.addstr(2,26," Arch. ")
    scr.addstr(2,35," Type ")
    scr.addstr(2,44," Pri: ")
    
    
    #scr.addstr(y_max-3,15," --- Displaying 1-5 of 5 ---")
    
    scr.addstr(y_max-1,2,"J/K: Up/Down   DEL: Remove")

## "Active" displays (client status, queue stuffs)

def update_display_queue(scr):
    # Loop through local copy of queue and call print_Q_item
    for index,item in enumerate(queue):
        i,hashcode,pri = item
        output_Q_item(scr,index,get_hash_info(hashcode),pri)

def output_Q_item(scr,index,item,pri):
    # Prints item on line index of scr (index is queue index, not window line)
    if item[0] == 'Ubuntu':
       attr = curses.color_pair(COLOR_U)
    elif item[0] == 'Kubuntu':
       attr = curses.color_pair(COLOR_K) | curses.A_BOLD
    elif item[0] == 'Edubuntu':
       attr = curses.color_pair(COLOR_E) | curses.A_BOLD
    elif item[0] == 'Xubuntu':
       attr = curses.color_pair(COLOR_X) | curses.A_BOLD
    
    if item[1][0:4] == '6.06':
        ver = 'D'
    elif item[1] == '6.10':
        ver = 'E'
    elif item[1] == '7.04':
        ver = 'F'
    elif item[1] == '7.10':
        ver = 'G'
    elif item[1][0:4] == '8.04':
        ver = 'H'
    elif item[1] == '8.10':
        ver = 'I'
    elif item[1] == '9.04':
        ver = 'J'

    scr.addstr(index+2,3,"          ")
    scr.addstr(index+2,3,item[0][0:1],attr)
    scr.addstr(index+2,5,ver)
    scr.addstr(index+2,7,item[2][0:1])
    scr.addstr(index+2,9,item[3][0:1])
    scr.addstr(index+2,11,str(pri))


def update_display_clients(scr):
    # Loop through local copy of clients and call output_client
    for i in range(0,6):
        output_client_clear(scr,i)
    for i in range(0,len(clients)):
        output_client(scr,i,clients[i])

def output_client(scr,index,client):
#   logging.debug('output: ' + client[3])
    if client[3].count('\t') < 1: # Things without a tab, I don't think anything still does
        hashcode = 'x'
        status = client[3]
    else:
        hashcode,status = client[3].split(COM_DELIM) # hash,status
        
    if ubuntudisc.is_hash(hashcode):
        tup = ubuntudisc.hash2Tuple(hashcode)
        disc = UbuntuDisc(tup[0], tup[1], tup[2], tup[3])
        
        f_str = ubuntudisc.FLAVOR_NAMES[disc.flavor]
        e_str = ubuntudisc.EDITION_NAMES[disc.edition]
        a_str = ubuntudisc.ARCHITECTURE_NAMES[disc.architecture]
        
        if disc.flavor == ubuntudisc.UBUNTU:
           attr = curses.color_pair(COLOR_U)
        elif disc.flavor == ubuntudisc.KUBUNTU:
           attr = curses.color_pair(COLOR_K) | curses.A_BOLD
        elif disc.flavor == ubuntudisc.EDUBUNTU:
           attr = curses.color_pair(COLOR_E) | curses.A_BOLD
        elif disc.flavor == ubuntudisc.XUBUNTU:
           attr = curses.color_pair(COLOR_X) | curses.A_BOLD
        
        # modified this to reflect our current SCaLE repitoire
        if disc.version == ubuntudisc.V_8_10:
            ver = 'I'
        elif disc.version == ubuntudisc.V_8_04_2:
            ver = 'H'
        elif disc.version == ubuntudisc.V_8_04_1:
            ver = 'H'

        scr.addstr(1,index*11+1,f_str[0:1],attr)
        scr.addstr(1,index*11+3,ver)
        scr.addstr(1,index*11+5,e_str[0:1])
        scr.addstr(1,index*11+7,a_str[0:1])

        #Now check Status
        attr = 0
        prog = "?"
        if status == '0':
            attr |= 0
            prog = '0%'
        elif status == '25':
            attr |= curses.A_REVERSE
            prog = '25%'
        elif status == '50':
            attr |= curses.A_REVERSE
            prog = '50% '
        elif status == '75':
            attr |= curses.A_REVERSE
            prog = '75%   '
        elif status == '100': #Time won't come through (stopped at server)
            attr |= curses.A_REVERSE
            prog = ' VERIFY '
        elif status == 'PASS':
            attr |= curses.color_pair(COLOR_PASS) | curses.A_BOLD
            prog = '* PASS *'
        elif status == 'FAIL':
            attr |= curses.color_pair(COLOR_FAIL) | curses.A_BOLD
            prog = '! FAIL !'
            
        scr.addstr(2,index*11+1,prog,attr)

    else: # not a hash, must be AVAIL|EMPTY|OPEN # These will be status, hash will be disk/drive type (CDR|DVD)
        # Need some way to *ask* for a DVD instead of a CD
        attr = 0
        if status == 'OPEN':
            attr |= 0
            stat = 'OPEN'
        elif status == 'AVAIL':
            attr |= 0
            stat = '* AVAIL '
        elif status == 'EMPTY':
            attr |= 0
            stat = '* EMPTY '

        scr.addstr(2,index*11+1,stat,attr)

    scr.addnstr(0,index*11+1,client[1],9) # All clients have names


def output_client_clear(scr,index):
    for i in range(0,3):
        scr.addstr(i,index*11,'          ')

def get_queue(): # Dummy Queue Population
    queue.append(('12b4','5'))
    queue.append(('1231','7'))
    queue.append(('1233','10'))
    queue.append(('1232','15'))
    queue.append(('b0cf','1'))

def get_clients(): # Dummy Client Population
    # ID, Name, Type, Status # image is included in status... is type as well?
    clients.append(('033312ebed6b1e5c5a691fd6e24f7532','Client0','CDR','1231231231231231231234\t0'))
    #clients.append(('033312ebed6b1e5c5a691fd6e24f7532','Client0','CDR','AVAIL'))
    clients.append(('033312ebed6b1e5c5a691fd6e24f7539','Client12345678','CDR','12312312312312312311237\t25'))
    #clients.append(('033312ebed6b1e5c5a691fd6e24f7539','Client12345678','CDR','EMPTY'))
    clients.append(('033312ebed6b1e5c5a691fd6e24f7531','Client2','CDR','1231231231231231231231\t50'))
    #clients.append(('033312ebed6b1e5c5a691fd6e24f7531','Client2','CDR','OPEN'))
    clients.append(('033312ebed6b1e5c5a691fd6e24f7536','Client3','CDR','1231231231231231232\t100'))
    clients.append(('033312ebed6b1e5c5a691fd6e24f7532','Client4','CDR','1231231231231231236\tPASS'))
    clients.append(('033312ebed6b1e5c5a691fd6e24f7535','Client5','CDR','1231231231231231230\tFAIL'))

def update_menu_order(scr):
    # order modes: pkg, custom, submit
    global order_cursor, keysdown, order_spinner_indices, order_mode, selected_pkg
    global alert_text, target_time
    
    # handle mode reset
    if order_mode == 3 and time.time() >= target_time:
        curses.flash()
        order_cursor = 0
        order_mode = 0
        alert_text = ""
    
    if keysdown[KEY_DOWN]:
        order_cursor += 1
    elif keysdown[KEY_UP]:
        order_cursor -= 1
    elif keysdown[KEY_LEFT]:
        if order_mode == 1:
            order_spinner_indices[order_cursor] -= 1
    elif keysdown[KEY_RIGHT]:
        if order_mode == 1:
            order_spinner_indices[order_cursor] += 1
    elif keysdown[KEY_CONFIRM]:
        if order_mode == 0: # Package was selected
            pkgid = order_cursor
            selected_pkg = pkgid
            if pkgid == 0:
                order_mode = 1
            else:
                order_mode = 2
                order_cursor = 0
        elif order_mode == 1: # Custom CD configured
            order_mode = 2
            order_cursor = 0
        elif order_mode == 2: # Decision made
            if order_cursor == 0: # Reset Pressed
                order_mode = 0
                order_cursor = 0
                selected_pkg = 0
                alert_text = ""
            elif order_cursor == 1: # Submit pressed
                # make the correct order
                if selected_pkg == 0: # custom cd
                    f = order_spinner_indices[0] % num_flavors
                    v = order_spinner_indices[1] % num_versions
                    a = order_spinner_indices[2] % num_architectures
                    e = order_spinner_indices[3] % num_editions
                    q = 1
                    p = 50 # default vals
                    q_str = get_console_string(scr, "Quantity: ", 10, 36, 4)
                    p_str = get_console_string(scr, "Priority: ", 11, 36, 4)
                    
                    if len(q_str) > 0:
                        q = int(q_str)
                    
                    if len(p_str) > 0:
                        p = int(p_str)
                    
                    rtn = submit_order(f,v,a,e,q,p)
                    if rtn is True:
                        alert_text = "Custom CD Order Submitted!"
                    else:
                        alert_text = "ERR: This CD config is not available!"
                else:
                    submit_package_order(selected_pkg)
                    alert_text = "Package Order Submitted!"
                
                order_mode = 3
                target_time = time.time() + 2      
            
    
    # handle cursor wrap-around logic and other misc. stuff
    if order_mode == 0:
        if order_cursor > len(packages) - 1:
            order_cursor = len(packages) - 1
        elif order_cursor < 0:
            order_cursor = 0
    elif order_mode == 1:
        order_cursor %= 6
    elif order_mode == 2:
        order_cursor %= 2

def update_menu_packages(scr):
    global packages_cursor, keysdown
    
    if keysdown[KEY_DOWN]:
        packages_cursor += 1
    elif keysdown[KEY_UP]:
        packages_cursor -= 1
    elif keysdown[KEY_INSERT]:
        name = get_console_string(scr, "Title: ", 14, 2, 32)
        #add_package(name)
    elif keysdown[KEY_DELETE]:
        jess_is_awesome = True # why doesnt python like empty elifs at the end of a function?
        #delete_package(packages_cursor % len(packages))

def update_menu_clients(scr):
    global clients_cursor, keysdown
    
    if keysdown[KEY_DOWN]:
        clients_cursor += 1
    elif keysdown[KEY_UP]:
        clients_cursor -= 1 
    elif keysdown[KEY_EJECT]:
        eject_client(clients_cursor % len(clients))
    elif keysdown[KEY_RENAME]:
        newname = get_console_string(scr, "Rename: ", 14, 2, 8)
        
        rename_client(clients_cursor % len(clients), newname)
                 

def update_menu_queue(scr):
    global queue_cursor, keysdown
    
    if keysdown[KEY_DOWN]:
        queue_cursor += 1
    elif keysdown[KEY_UP]:
        queue_cursor -= 1
    elif keysdown[KEY_DELETE]:
        if len(queue) > 0:
            delete_from_queue(queue_cursor % len(queue))

def update_tab(i):
    if i == 0:
        update_menu_order(tabs[i])
        draw_menu_order(tabs[i])
        draw_tabs(tabs[i],tabnames,i)
    elif i == 1:
        update_menu_packages(tabs[i])
        draw_menu_packages(tabs[i])
        draw_tabs(tabs[i],tabnames,i)
    elif i == 2:
        update_menu_clients(tabs[i])
        draw_menu_clients(tabs[i])
        draw_tabs(tabs[i],tabnames,i)
    elif i == 3:
        update_menu_queue(tabs[i])
        draw_menu_queue(tabs[i])
        draw_tabs(tabs[i],tabnames,i)

def handle_input(scr):
    global active_tab
    global is_running
    global keysdown
    
    code = scr.getch()
    if (code == curses.ERR): # If no keypress, move on to next loop
        return
    key = curses.keyname(code) # convert to printable (readable keycaps)
    if key == '^[': # meta (alt)? get *one* more char (this may be wrong?) More?
        ch = scr.getch()
        if (ch != curses.ERR): # Its a real character
            code = 255 * code + ch # Add them (16 bits)
            key = key + curses.keyname(ch) # concat
    
    #sp = 32 tab = 9
    if key == 'q': # quit!
        is_running = False
    elif key == '^[1': # alt-1
        active_tab = 0
        # Reset whatever state tab 0 is in?
    elif key == '^[2':
        active_tab = 1
        #Reset tab 1
    elif key == '^[3':
        active_tab = 2
        #Reset tab 2
    elif key == '^[4': # alt-4
        active_tab = 3
    elif key == 'z':
        queue.append(queue.pop(0))
        stale_queue = True
        #Reset Tab 3
    elif code in (ord('h'), curses.KEY_UP):
        keysdown[KEY_UP] = 1
    elif code in (ord('l'), curses.KEY_DOWN):
        keysdown[KEY_DOWN] = 1
    elif code in (ord('j'), curses.KEY_LEFT):
        keysdown[KEY_LEFT] = 1
    elif code in (ord('k'), curses.KEY_RIGHT):
        keysdown[KEY_RIGHT] = 1
    elif code == 10: # Enter key
        keysdown[KEY_CONFIRM] = 1
    elif code == 27: # Esc key
        keysdown[KEY_CANCEL] = 1
    elif code == 330: # Del key
        keysdown[KEY_DELETE] = 1
    elif key == 'e': # Eject key
        keysdown[KEY_EJECT] = 1
    elif key == 'r': # Rename key
        keysdown[KEY_RENAME] = 1
    elif key == 'i': # Insert key
        keysdown[KEY_INSERT] = 1
    
    else:
        scr.addstr(22, 3, str(code))
        curses.flash() # Flash on non-mapped key

def clear_keys():
    global keysdown
    for i in range(12):
        keysdown[i] = 0
                    
## Main stuffs

def main(stdscr):
    curses.curs_set(0) # hide cursor
    curses.init_pair(1,curses.COLOR_YELLOW,curses.COLOR_BLACK) # Ubuntu (Yellow?)
    curses.init_pair(2,curses.COLOR_BLUE,curses.COLOR_BLACK) # Kubuntu Blue on Black
    curses.init_pair(3,curses.COLOR_RED,curses.COLOR_BLACK) # Edubuntu
    curses.init_pair(4,curses.COLOR_CYAN,curses.COLOR_BLACK) # Xubuntu
    curses.init_pair(5,curses.COLOR_BLACK,curses.COLOR_GREEN) # Pass
    curses.init_pair(6,curses.COLOR_BLACK,curses.COLOR_RED) # Fail (This could be reverse edubuntu)

    """while (1):
        try:
            server.connect((HOST, PORT))
            break
        except socket.error:
            # Since non-blocking, if it doesn't work immediately, EINPROGRESS
            # Subsequent calls (while in progress) give EALREADY
            # There are other errors (actual errors), we may want to check them
            pass"""

    stdscr.bkgd('*', curses.A_REVERSE )
    win_sidebar = curses.newwin(21,15,0,0)
    # Set up sidebar (static stuff) UGLY CHANGE!!!!!!!!!!!!! - JB
    win_sidebar.border(' ','|',' ',' ',' ',curses.ACS_VLINE,' ',curses.ACS_VLINE) # Righthand Line
    win_sidebar.addstr(0,0,"    Queue     ", curses.A_UNDERLINE)
    win_sidebar.addstr(1,3,"F V A T P")
    for i in range(1,10):
        win_sidebar.addstr(i+1,1,str(i))
    for i in range(10,20):
        win_sidebar.addstr(i+1,0,str(i))
    # done with sidebar static stuff

    win_topbar = curses.newwin(4,65,0,15)
    # set up top bar (static stuff)
    win_topbar.border(' ',' ',' ','-',' ',' ','-','-') # Bottom Line
    for i in range(1,6):
        for j in range(0,3):
            win_topbar.addstr(j,i*11-1,'|') # Dividers between clients
        win_topbar.addstr(0,i*11,' ******** ') # blank client names (2-6)
    win_topbar.addstr(0,0,' ******** ') # blank client name (1)
    # done with top bar static stuff

    # Now we set up the four (up to five) tabs
    tabs.append(curses.newwin(17,65,4,15))  # These panel references are
    tabs.append(curses.newwin(17,65,4,15))  # important, without them
    tabs.append(curses.newwin(17,65,4,15))  # our panels get GC'd
    tabs.append(curses.newwin(17,65,4,15))  # Using Win instead?

    # Put some test stuff in the tabs
    draw_menu_order(tabs[0])
    draw_menu_packages(tabs[1])
    draw_menu_clients(tabs[2])
    draw_menu_queue(tabs[3])

    # initial updates
    #get_queue()
    #get_clients()
    update_package_names()
    

    global active_tab
    global is_running
    global keysdown
    global blankkeys
    global frame_count
    keysdown = blankkeys
    active_tab = 0
    stale_queue = True
    stale_client = True
    stdscr.nodelay(1)
    curses.meta(1)
    while(is_running):
        
        
        stdscr.noutrefresh()
        win_sidebar.noutrefresh()
        win_topbar.noutrefresh()
        tabs[active_tab].touchwin() # Have to make them think this is modified
        tabs[active_tab].noutrefresh()
        curses.doupdate()
        

        """# begin socket stuff
        try: #try RX
            if len(server.recv(1024,socket.MSG_PEEK)) == 0:
                server.close() # Bad connection, We likely want to reconnect
                continue
            # otherwise: do stuff with inbuf
            inbuf = inbuf + server.recv(1024)
        except socket.error: # Excepion (no data RX, but connection still there)
            pass

        if len(outbuf) > 0: # if we have stuff to send
            try: # try TX
                sent = server.send(outbuf)
                outbuf = outbuf[sent:]
            except socket.error: # We only want to catch SIGPIPE (server disconnect)
                pass
        # done with socket stuff"""


        # Handle Communication
        if stale_queue:
            update_display_queue(win_sidebar)
            stale_queue = False
        if stale_client:
            update_display_clients(win_topbar)
            stale_client = False


        handle_input(stdscr)
        update_tab(active_tab)
        
        #clear keys
        clear_keys()
        frame_count += 1



curses.wrapper(main)


# window.nodelay(true)

