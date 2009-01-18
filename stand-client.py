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

tabnames = ("Order","Packages","Clients","Queue","")
tabs = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0) # non-blocking

inbuf = ''
outbuf = ''

## Socket Functions

def get_ident():
    # Figure out someway to generate
    # Maybe md5 of MAC address and /dev/sdX or something?
    # Persistence only matters for burners, so we can use 
    # pseudo-random for command/display
    return '033312ebed6b1e5c5a691fd6e24f7535'


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
    scr.addstr(4,19,"[ NEW ]")
    scr.addstr(5,19,"MM.YY  ",curses.A_UNDERLINE)
    scr.addstr(6,19,"[ OLD ]")
    #Arch
    scr.addstr(4,28,"[ ] i386")
    scr.addstr(5,28,"[ ] AMD64")
    #Type
    scr.addstr(3,40,"[ ] Desktop")
    scr.addstr(4,40,"[ ] Alternate")
    scr.addstr(5,40,"[ ] Server")
    #Quantity/Priority
    scr.addstr(3,56,"Qty: ")
    scr.addstr(3,61,"  ",curses.A_UNDERLINE)
    scr.addstr(5,56,"Pri: ")
    scr.addstr(5,61,"  ",curses.A_UNDERLINE)

    # Submits, Clear
    scr.addstr(y_max-2,2,"[ Submit Single ]")
    scr.addstr(y_max-2,25,"[ Submit Package ]")
    scr.addstr(y_max-2,50,"[ Reset ]")

    

def main(stdscr):
    curses.curs_set(0) # hide cursor
    curses.init_pair(1,curses.COLOR_YELLOW,curses.COLOR_BLACK) # Ubuntu (Yellow?) Magenta?
    curses.init_pair(2,curses.COLOR_BLUE,curses.COLOR_BLACK) # Kubuntu Blue on Blank
    curses.init_pair(3,curses.COLOR_RED,curses.COLOR_BLACK) # Edubuntu
    curses.init_pair(4,curses.COLOR_CYAN,curses.COLOR_BLACK) # Xubuntu

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
    #tabs[0].addstr(2,2,"This tab is where you ask for stuff")
    do_menu_order(tabs[0])
    tabs[1].addstr(3,2,"This tab is for modifying packages")
    tabs[2].addstr(4,2,"This tab modifies client information")
    tabs[3].addstr(5,2,"This tab lets you modify the queue directly")

    active_tab = 0
    stdscr.nodelay(1)
    curses.meta(1)
    while(1):

        stdscr.noutrefresh()
        win_sidebar.noutrefresh()
        win_topbar.noutrefresh()
        tabs[active_tab].touchwin() # Have to make them think this is modified
        tabs[active_tab].noutrefresh()
        curses.doupdate()

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
        elif key == '^[2':
            active_tab = 1
        elif key == '^[3':
            active_tab = 2
        elif key == '^[4': # alt-4
            active_tab = 3
        elif key == 'r':
            fg,bg = curses.pair_content(1)
            fg += 1
            fg %= curses.COLORS
            curses.init_pair(1,fg,bg)
        elif key == 'f':
            fg,bg = curses.pair_content(1)
            fg -= 1
            fg %= curses.COLORS
            curses.init_pair(1,fg,bg)
        elif key == 'p':
            fg,bg = curses.pair_content(1)
            bg += 1
            bg %= curses.COLORS
            curses.init_pair(1,fg,bg)
        elif key == 'l':
            fg,bg = curses.pair_content(1)
            bg -= 1 
            bg %= curses.COLORS
            curses.init_pair(1,fg,bg)
        else:
            curses.flash() # Flash on non-mapped key



curses.wrapper(main)


# window.nodelay(true)

