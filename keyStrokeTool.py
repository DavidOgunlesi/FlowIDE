from curses import wrapper

def main(stdscr):
	
	while True:
		key = stdscr.getch()
		stdscr.addstr(5,5,f"Key {chr(key)}: {key}")
		stdscr.refresh()

wrapper(main)
