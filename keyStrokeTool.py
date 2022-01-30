from curses import wrapper
import curses

def main(stdscr):
	curses.mousemask(2)
	while True:
		key = stdscr.getch()
		stdscr.addstr(5,5,f"Key {chr(key)}: {key}")
		stdscr.refresh()

wrapper(main)
