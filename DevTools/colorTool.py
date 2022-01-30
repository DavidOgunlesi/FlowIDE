import curses
from curses import wrapper

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, 255):
        curses.init_pair(i + 1, i, -1)
    try:
        for i in range(0, 255):
            stdscr.addstr(f"{i}: █", curses.color_pair(i+1))
    except curses.ERR:
        # End of screen reached
        pass
    stdscr.getch()

wrapper(main)
