from curses import wrapper
import curses

def main(stdscr):
	curses.mousemask(-1)
	curses_mouse_states = {
		curses.BUTTON1_PRESSED: 'Button 1 Pressed', 
		curses.BUTTON1_RELEASED: 'Button 1 Released', 
		curses.BUTTON1_CLICKED: 'Button 1 Clicked',
		curses.BUTTON1_DOUBLE_CLICKED: 'Button 1 Double-Clicked',
		curses.BUTTON1_TRIPLE_CLICKED: 'Button 1 Triple-Clicked',

		curses.BUTTON2_PRESSED: 'Button 2 Pressed', 
		curses.BUTTON2_RELEASED: 'Button 2 Released', 
		curses.BUTTON2_CLICKED: 'Button 2 Clicked',
		curses.BUTTON2_DOUBLE_CLICKED: 'Button 2 Double-Clicked',
		curses.BUTTON2_TRIPLE_CLICKED: 'Button 2 Triple-Clicked',

		curses.BUTTON3_PRESSED: 'Button 3 Pressed', 
		curses.BUTTON3_RELEASED: 'Button 3 Released', 
		curses.BUTTON3_CLICKED: 'Button 3 Clicked',
		curses.BUTTON3_DOUBLE_CLICKED: 'Button 3 Double-Clicked',
		curses.BUTTON3_TRIPLE_CLICKED: 'Button 3 Triple-Clicked',

		curses.BUTTON4_PRESSED: 'Button 4 Pressed', 
		curses.BUTTON4_RELEASED: 'Button 4 Released', 
		curses.BUTTON4_CLICKED: 'Button 4 Clicked',
		curses.BUTTON4_DOUBLE_CLICKED: 'Button 4 Double-Clicked',
		curses.BUTTON4_TRIPLE_CLICKED: 'Button 4 Triple-Clicked',

		curses.BUTTON_SHIFT: 'Button Shift', 
		curses.BUTTON_CTRL: 'Button Ctrl', 
		curses.BUTTON_ALT: 'Button Alt'
	}
	while True:
		key = stdscr.getch()
		stdscr.clear()
		if key == curses.KEY_MOUSE:
			mouse_state = curses.getmouse()[4]
			states = '; '.join(state_string for state, state_string in curses_mouse_states.items() if mouse_state & state)
			stdscr.addstr(5,5,f"Mouse: {states} with id {mouse_state}")
			stdscr.refresh()#2097152
			continue
		stdscr.addstr(5,5,f"Key {chr(key)}: {key}")
		stdscr.refresh()

wrapper(main)
