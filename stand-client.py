#!/usr/bin/env python

import curses
import curses.wrapper
import curses.panel
import curses.ascii

import socket

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

keysdown = []
blankkeys = [0,0,0,0,0,0,0,0,0,0]

KEYCODE_UP = 'h'
KEYCODE_DOWN = 'l'
KEYCODE_LEFT = 'j'
KEYCODE_RIGHT = 'k'
KEYCODE_CONFIRM = 'ENTER'
KEYCODE_CANCEL = 'CANCEL'
KEYCODE_EJECT = 'e'
KEYCODE_RENAME = 'r'

order_cursor = 0
order_mode = 0
order_spinner_indices = [0,0,0,0,0,0]

packages_cursor = 0

clients_cursor = 0

queue_cursor = 0

flavors = ["Ubuntu", "Kubuntu", "Edubuntu", "Xubuntu"]
versions = ["8.04.2", "8.10"]
architectures = ["i386", "AMD64"]
types = ["Desktop", "Server", "Alternate"]
packages = ["Custom CD", "Package B", "Package C", "Package D", "Package E", "Package F", "Package G", "Package H"]

active_tab = 0
is_running = True
tabnames = ("Order","Packages","Clients","Queue","")
tabs = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0) # non-blocking

clients = []
# clients are a tuple of ID,Name,type,status # type includes hash
queue = []
# Queue items are tuples of hash,priority
# or do we want to do flavor,arch,version,yadda,yadda,priority?

inbuf = ''
outbuf = ''

## Socket Functions

def get_ident(): # Return our client ID
    # Figure out someway to generate
    # Maybe md5 of MAC address and /dev/sdX or something?
    # Persistence only matters for burners, so we can use 
    # pseudo-random for command/display
    return '033312ebed6b1e5c5a691fd6e24f7535'

def is_hash(str):
    if len(str) == 32:
        for ch in str:
            if ch not in "0123456789abcdef":
                return False
        return True
    return False


# CD info stuff
def get_hash_info(hash): # Dummy
    info = [('Ubuntu','8.04.1','AMD64','Desktop'),('Kubuntu','8.10','i386','Alternate'),
            ('Xubuntu','6.06.2','i386','Server'),('Edubuntu','8.04.1','AMD64','Alternate')]
    index = int(hash,16) % len(info)
    return info[index]



## Curses Functions

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

def draw_scrollpane(scr, y, x, h, w, title, data, sel_index):
    start_row = 0
    if sel_index > h - 1:
        start_row = sel_index - h + 1
        
    end_row = start_row + h
    if end_row > len(data):
        end_row = len(data)
    
    attr = 0
    make_box(scr, y, x, h, w)
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

# The Orders Tab
def draw_menu_order(scr): # Do the static page stuff for Order page
    
    scr.erase()
    y_max,x_max = scr.getmaxyx()
    selected_pkg = order_cursor
    if order_mode == 1:
        selected_pkg = 0
    draw_scrollpane(scr, 2, 1, 5, 60, "CD Packages", packages, selected_pkg)
    #make_box(tabs[0],2,1,y_max-2-2-9,x_max-4)
    #scr.addstr(y_max,1,"X:" + str(x_max) + "Y:" + str(y_max))
    
    #scr.addstr(y_max//2,x_max//2,"*")

    # Single CD stuff
    indent = 9
    row = 10
    
    if order_mode == 1:
        scr.addstr(9,x_max/2-7," Single CD")
        
        # Flavor
        draw_spinner(scr, row, indent, "Flavor:", flavors[order_spinner_indices[order_cursor] % len(flavors)], (order_cursor == 0))
        #scr.addstr(3,indent+11,"E",curses.color_pair(COLOR_E))
        
        # Version
        draw_spinner(scr, row+1, indent, "Version:", "8.10", (order_cursor == 1))
        
        # Architecture
        draw_spinner(scr, row+2, indent, "Arch:", "i386", (order_cursor == 2))
        
        # Type
        draw_spinner(scr, row+3, indent, "Type:", "Alternate", (order_cursor == 3))
        
        # Quantity
        draw_spinner(scr, row, indent+27, "Quantity:", "1", (order_cursor == 4), 11, 5)
        
        # Priority
        draw_spinner(scr, row+1, indent+27, "Priority:", "1", (order_cursor == 5), 11, 5)

    # Submits, Clear
    scr.addstr(y_max-2,10,"[ Submit Order ]")
    scr.addstr(y_max-2,35,"[ Reset ]")
    
    scr.addstr(14, 4, str(order_cursor))

# The Packages Tab
def draw_menu_packages(scr):
    scr.erase()
    scr.addstr(3,2,"This tab is for modifying packages")

# The Clients Tab
def draw_menu_clients(scr):
    scr.erase()
    num_clients = 6
    client_names = ["JESS", "FLANNEL", "NHAINES", "YASUMOTO", "LIKETOTA", ""]
    client_ip = ["X.X.128.87", "X.X.128.92", "X.X.128.33", "X.X.128.103", "X.X.128.79", ""]
    client_jobs = ["Ubuntu 8.10 i386 Dsk.", "Kubuntu 8.10 i386 Dsk.", "Edubuntu 8.10 i386 Srv.", "", "Ubuntu 8.10 i386 Alt.", ""]
    client_status = ["BURNING (87%)", "TEST PASSED", "VERIFYING", "AWAITING MEDIA", "BURNING (8%)", "NO CLIENT"]
    selected_client = 0
    
    y_max,x_max = scr.getmaxyx()
    width = 32
    height = 4
    
    
    for i in range(num_clients):
        row = i / 2
        col = 0 if i % 2 == 0 else 1
        posy = (row * height)+2
        posx = (col * width)
        
        attr = curses.color_pair(COLOR_X) | curses.A_BOLD if i == selected_client else 0
        make_box(tabs[2],posy,posx,2,30, attr)
        scr.addstr(posy, posx+2, client_names[i], attr)
        scr.addstr(posy, posx+15, client_ip[i], attr)
        scr.addstr(posy+1, posx+1, "Job: " + client_jobs[i])
        scr.addstr(posy+2, posx+1, "Status: " + client_status[i])
    
    scr.addstr(y_max-3,15," --- Displaying 1-6 of 6 ---")
    
    scr.addstr(y_max-1,2,"J/K: Up/Down   H/L: Left/Right   E: Eject    R: Rename")

def draw_menu_queue(scr, update=0):
    scr.erase()
    queue_len = 5
    distros = ["Edubuntu", "Ubuntu", "Kubuntu", "Xubuntu", "Ubuntu"]
    versions = ["8.10", "8.04", "7.10", "8.10", "8.10"]
    architectures = ["i386", "i386", "PPC", "AMD", "i386"]
    types = ["Alt.", "Dsk.", "Srv.", "Dsk.", "Dsk"]
    priorities = ["5", "7", "10", "11", "30"]
    selected_item = 0
    
    y_max,x_max = scr.getmaxyx()
    offset = 2
    make_box(tabs[3],2,1,y_max-2-2-3,x_max-4)
    scr.addstr(2,2,"# ")
    scr.addstr(2,6," Distro ")
    scr.addstr(2,18," Ver. ")
    scr.addstr(2,26," Arch. ")
    scr.addstr(2,35," Type ")
    scr.addstr(2,44," Pri: ")
    if update == 1:
        scr.addstr(2,44," Jess: ")
    
    for i in range(queue_len):
        
        if i == selected_item:
            attr = curses.A_REVERSE
            scr.addstr(i+3, offset, " " * 60, attr)
        else:
            attr = 0
        
        scr.addstr(i+3, offset, str(i+1)+".", attr)
        scr.addstr(i+3, offset+5, distros[i], attr)
        scr.addstr(i+3, offset+17, versions[i], attr)
        scr.addstr(i+3, offset+25, architectures[i], attr)
        scr.addstr(i+3, offset+34, types[i], attr)
        scr.addstr(i+3, offset+43, priorities[i], attr)
    
    scr.addstr(y_max-3,15," --- Displaying 1-5 of 5 ---")
    
    scr.addstr(y_max-1,2,"J/K: Up/Down   DEL: Remove   +/-: Priority")

## "Active" displays (client status, queue stuffs)

def update_display_queue(scr):
    # Loop through local copy of queue and call print_Q_item
    for index,item in enumerate(queue):
        hash,pri = item
        output_Q_item(scr,index,get_hash_info(hash),pri)

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
    scr.addstr(index+2,11,pri)


def update_display_clients(scr):
    # Loop through local copy of clients and call output_client
    for i in range(0,6):
        output_client_clear(scr,i)
    for i in range(0,len(clients)):
        output_client(scr,i,clients[i])

def output_client(scr,index,client):
#   logging.debug('output: ' + client[3])
    if client[3].count('\t') < 1: # Things without a tab, I don't think anything still does
        hash = 'x'
        status = client[3]
    else:
        hash,status = client[3].split(COM_DELIM) # hash,status
    if is_hash(hash):
        item = get_hash_info(hash) 
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

        scr.addstr(1,index*11+1,item[0][0:1],attr)
        scr.addstr(1,index*11+3,ver)
        scr.addstr(1,index*11+5,item[2][0:1])
        scr.addstr(1,index*11+7,item[3][0:1])

        #Now check Status
        attr = 0
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

def update_menu_order():
    # order modes: pkg, custom, submit
    global order_cursor, keysdown, order_spinner_indices, order_mode
    
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
        pkgid = order_cursor
        if pkgid == 0:
            order_mode = 1
        else:
            order_mode = 2
    
    
    if order_mode == 0:
        if order_cursor > len(packages) - 1:
            order_cursor = len(packages) - 1
        elif order_cursor < 0:
            order_cursor = 0
    elif order_mode == 1:
        order_cursor %= 6

def update_tab(i):
    if i == 0:
        update_menu_order()
        draw_menu_order(tabs[i])
        draw_tabs(tabs[i],tabnames,i)
    elif i == 1:
        draw_menu_packages(tabs[i])
        draw_tabs(tabs[i],tabnames,i)
    elif i == 2:
        draw_menu_clients(tabs[i])
        draw_tabs(tabs[i],tabnames,i)
    elif i == 3:
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
    else:
        scr.addstr(22, 3, str(code))
        curses.flash() # Flash on non-mapped key

def clear_keys():
    global keysdown
    for i in range(10):
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

    stdscr.bkgd('*', curses.A_REVERSE )
    win_sidebar = curses.newwin(21,15,0,0)
    # Set up sidebar (static stuff)
    win_sidebar.border(' ',curses.ACS_VLINE,' ',' ',' ',curses.ACS_VLINE,' ',curses.ACS_VLINE) # Righthand Line
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

    # Dummy stuff
    get_queue()
    get_clients()

    global active_tab
    global is_running
    global keysdown
    global blankkeys
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



curses.wrapper(main)


# window.nodelay(true)

