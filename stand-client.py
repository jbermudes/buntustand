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
    if len(str) > 10: # This can be done better, obviously
        return True
    return False

# CD info stuff
def get_hash_info(hash): # Dummy
    info = [('Ubuntu','8.04.1','AMD64','Desktop'),('Kubuntu','8.10','i386','Alternate'),
            ('Xubuntu','6.06.2','i386','Server'),('Edubuntu','8.04.1','AMD64','Alternate')]
    index = int(hash,16) % len(info)
    return info[index]



## Curses Functions

def make_box(scr,y,x,h,w): # y,x is top left corner (of border), h,w is empty space inside
    for i in range(y+1,y+h+1):
        scr.addch(i,x,curses.ACS_VLINE)
        scr.addch(i,x+w+1,curses.ACS_VLINE)

    for i in range(x+1,x+w+1):
        scr.addch(y,i,curses.ACS_HLINE)
        scr.addch(y+h+1,i,curses.ACS_HLINE)

    scr.addch(y,x,curses.ACS_ULCORNER)
    scr.addch(y,x+w+1,curses.ACS_URCORNER)
    scr.addch(y+h+1,x,curses.ACS_LLCORNER)
    scr.addch(y+h+1,x+w+1,curses.ACS_LRCORNER)


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

def do_menu_order(scr): # Do the static page stuff for Order page
    #tabs[0].addstr(2,2,"This tab is where you ask for stuff")
    y_max,x_max = scr.getmaxyx()
    make_box(tabs[0],8,1,y_max-2-2-8,x_max-4)
    #scr.addstr(y_max,1,"X:" + str(x_max) + "Y:" + str(y_max))
    scr.addstr(2,x_max/2-4,"Single CD")
    scr.addstr(8,x_max/2-6," CD Packages ")
    #scr.addstr(y_max//2,x_max//2,"*")

    # Single CD stuff
    # Flavor
    scr.addstr(3,3,"[ ] Ubuntu")   # U
    scr.addstr(3,7,"U",curses.color_pair(COLOR_U))
    scr.addstr(4,3,"[ ] Kubuntu")  # K
    scr.addstr(4,7,"Ku",curses.color_pair(COLOR_K)|curses.A_BOLD)
    scr.addstr(5,3,"[ ] Xubuntu")  # X
    scr.addstr(5,7,"Xu",curses.color_pair(COLOR_X)|curses.A_BOLD)
    scr.addstr(6,3,"[ ] Edubuntu") # Edu
    scr.addstr(6,7,"Edu",curses.color_pair(COLOR_E)|curses.A_BOLD)
    #Version
    scr.addstr(4,18,"[ NEW ]")
    scr.addstr(5,18,"MM.YY  ",curses.A_UNDERLINE)
    scr.addstr(6,18,"[ OLD ]")
    #Arch
    scr.addstr(4,27,"[ ] i386")
    scr.addstr(5,27,"[ ] AMD64")
    #Type
    scr.addstr(3,39,"[ ] Desktop")
    scr.addstr(4,39,"[ ] Alternate")
    scr.addstr(5,39,"[ ] Server")
    #Quantity/Priority
    scr.addstr(3,55,"Qty: ")
    scr.addstr(3,60,"  ",curses.A_UNDERLINE)
    scr.addstr(5,55,"Pri: ")
    scr.addstr(5,60,"  ",curses.A_UNDERLINE)

    # Submits, Clear
    scr.addstr(y_max-2,2,"[ Submit Single ]")
    scr.addstr(y_max-2,25,"[ Submit Package ]")
    scr.addstr(y_max-2,50,"[ Reset ]")

def do_menu_packages(scr):
    scr.addstr(3,2,"This tab is for modifying packages")

def do_menu_clients(scr):
    scr.addstr(4,2,"This tab modifies client information")

def do_menu_queue(scr):
    scr.addstr(5,2,"This tab lets you modify the queue directly")

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
    if client[3].count('\t') < 1: # Things without a tab, those things are status
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

    else: # not a hash, must be AVAIL|EMPTY|OPEN # These will be status, hash will be 'x'
        # Itd be nice to not have to swap avail|empty and CDR|DVD.  Swap protocols to make that happen
        attr = 0 # Need some way to *ask* for a DVD instead of a CD
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

    for i in range(0,len(tabs)):
        #tabs[i].bkgd(' ',curses.color_pair(1))
        draw_tabs(tabs[i],tabnames,i)

    # Put some test stuff in the tabs
    do_menu_order(tabs[0])
    do_menu_packages(tabs[1])
    do_menu_clients(tabs[2])
    do_menu_queue(tabs[3])

    # Dummy stuff
    get_queue()
    get_clients()

    active_tab = 0
    stale_queue = True
    stale_client = True
    stdscr.nodelay(1)
    curses.meta(1)
    while(1):

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


        # Handle user Input
        code = stdscr.getch()
        if (code == curses.ERR): # If no keypress, move on to next loop
            continue
        key = curses.keyname(code) # convert to printable (readable keycaps)
        if key == '^[': # meta (alt)? get *one* more char (this may be wrong?) More?
            ch = stdscr.getch()
            if (ch != curses.ERR): # Its a real character
                code = 255 * code + ch # Add them (16 bits)
                key = key + curses.keyname(ch) # concat
 
        if key == 'q': # quit!
            break
#       elif code == curses.KEY_LEFT:
#           active_tab -= 1
#           active_tab %= 4
#       elif code == curses.KEY_RIGHT:
#           active_tab += 1
#           active_tab %= 4
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
#       elif key == 'r':
#           fg,bg = curses.pair_content(1)
#           fg += 1
#           fg %= curses.COLORS
#           curses.init_pair(1,fg,bg)
#       elif key == 'f':
#           fg,bg = curses.pair_content(1)
#           fg -= 1
#           fg %= curses.COLORS
#           curses.init_pair(1,fg,bg)
#       elif key == 'p':
#           fg,bg = curses.pair_content(1)
#           bg += 1
#           bg %= curses.COLORS
#           curses.init_pair(1,fg,bg)
#       elif key == 'l':
#           fg,bg = curses.pair_content(1)
#           bg -= 1 
#           bg %= curses.COLORS
#           curses.init_pair(1,fg,bg)
        else:
            curses.flash() # Flash on non-mapped key



curses.wrapper(main)


# window.nodelay(true)

