#!/usr/bin/env python

import curses
import curses.wrapper
import curses.panel
import curses.ascii

tabnames = ("Order","Packages","Clients","Queue")
tabs = []

def draw_tabs(scr,names,active):
    for i in range(0,65):
        scr.addstr(1,i,'-')
    for i in range(0,len(names)):
        scr.addstr(0,i*13+1,"/          \\")
        scr.addstr(0,i*13+3,tabnames[i])
    scr.addstr(1,active*13+1,"            ")

def toHex(s):
    lst = []
    for ch in s:
        hv = hex(ord(ch)).replace('0x', '')
        if len(hv) == 1:
            hv = '0'+hv
        lst.append(hv)
    
    return reduce(lambda x,y:x+y, lst)
   

def main(stdscr):
    curses.curs_set(0) # hide cursor
    curses.init_pair(1,curses.COLOR_WHITE,curses.COLOR_BLUE)
    curses.init_pair(2,curses.COLOR_BLUE,curses.COLOR_WHITE)

    stdscr.bkgd('*',curses.A_BOLD | curses.color_pair(2))
    win_sidebar = curses.newwin(21,15,0,0)
    # Set up sidebar (static stuff)
    win_sidebar.border(' ','|',' ',' ',' ','|',' ','|') # Righthand Line
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
        draw_tabs(tabs[i],tabnames,i)

    # Put some test stuff in the tabs
    tabs[0].addstr(2,2,"This tab is where you ask for stuff")
    tabs[1].addstr(3,2,"This tab is for modifying packages")
    tabs[2].addstr(4,2,"This tab modifies client information")
    tabs[3].addstr(5,2,"This tab lets you modify the queue directly")

#    for i in range(19,23): # For debugging purposes (so the key stands out)
#        for j in range(29,32):
#            stdscr.addstr(j,i,"-")

    active_tab = 0
#   stdscr.nodelay(1)
    curses.meta(1)
#    stdscr.keypad(1)
    stdscr.addstr(29,2,"ch:")
    stdscr.addstr(30,2,"keyname(ch):")
    stdscr.addstr(31,2,"unctrl(ch):")
    stdscr.addstr(32,2,"alt('1'):")
    while(1):

        stdscr.noutrefresh()
        win_sidebar.noutrefresh()
        win_topbar.noutrefresh()
        tabs[active_tab].touchwin() # Have to make them think this is modified
        tabs[active_tab].noutrefresh()
        curses.doupdate()

#        for i in range(19,61): # For debugging purposes (so the key stands out)
#            for j in range(29,33):
#                stdscr.addstr(j,i," ")
#        stdscr.noutrefresh()

        ch = stdscr.getch() # Raw character code
        if curses.ascii.ismeta(ch):
            stdscr.addstr(28,20,"Meta!")
        else:
            stdscr.addstr(28,20,"No!!?")
        stdscr.addstr(29,20,toHex(str(ch)))
        stdscr.addstr(29,40,str(ch))
        stdscr.addstr(28,30,curses.ascii.unctrl(ch))
        if ch == curses.ERR: # No keypress
            continue
        key = curses.keyname(ch) # convert to printable (readable keycaps)
        stdscr.addstr(28,35,curses.ascii.unctrl(ch)) #Debug
        stdscr.addstr(30,20,toHex(key))
        stdscr.addstr(28,40,curses.ascii.unctrl(ch)) #Debug
        stdscr.addstr(31,20,toHex(curses.ascii.unctrl(ch)))
        stdscr.addstr(28,45,curses.ascii.unctrl(ch)) #Debug
        stdscr.addstr(32,20,toHex(curses.ascii.alt('1')))
        stdscr.addstr(28,50,curses.ascii.unctrl(ch)) #Debug
        stdscr.addstr(30,40,key)
        stdscr.addstr(28,55,curses.ascii.unctrl(ch)) #Debug
        stdscr.addstr(31,40,curses.ascii.unctrl(ch))  # How on *earth* does this give us something different?
        stdscr.addstr(28,60,curses.ascii.unctrl(ch)) #Debug
        stdscr.addstr(32,40,curses.ascii.alt('1'))
        stdscr.addstr(28,65,curses.ascii.unctrl(ch)) #Debug
        if ch == curses.KEY_F5:
            active_tab = 0
        elif (toHex(curses.ascii.unctrl(ch)) == '315b'): # yes this is a hack -- And it doesn't even work
            active_tab = 1
        elif curses.ascii.unctrl(ch) == "2[":
            active_tab = 2
        elif key == 'M-4':
            active_tab = 3
        elif ch == curses.KEY_LEFT:
            active_tab -= 1
            active_tab %= 4
        elif ch == curses.KEY_RIGHT:
            active_tab += 1
            active_tab %= 4
        if key == 'q':
            break
 

        curses.flash()



curses.wrapper(main)


# window.nodelay(true)

