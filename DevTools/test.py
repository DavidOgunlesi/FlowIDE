import curses
import time
from curses import wrapper
from curses.textpad import Textbox, rectangle
#Init curses with wrapper
#Wrapper initialises curses for us

def TextBoxBehaviour(key):# L-452 U-450 R-454 D-456
	return key


#stdcr stands for standard screen, this is where all output is
def main(stdscr):
	#create a color pair
	curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_YELLOW)
	curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_YELLOW)
	#store in const
	BLUE_YELLOW = curses.color_pair(1)
	GREEN_YELLOW = curses.color_pair(2)

	'''stdscr.clear()'''
	#Place text at cursor (moves with every text place)
	'''stdscr.addstr("Hello World")'''
	#Place text on specific column and row
	'''stdscr.addstr(1,1,"Hello World")'''
	#text attribute
	'''stdscr.addstr(3,20,"Hello World", curses.A_DIM)'''
	#conbine attributes (| or operator commutative)
	'''stdscr.addstr(4,10,"Hello World", curses.A_REVERSE | BLUE_YELLOW)'''
	#All Other Attributes in Doc:
	#https://docs.python.org/3/library/curses.html

	#Creating window, windows have their own local coords
	#(height,width, row, col)
	#operattions on windows dont effect other windows or the main window(standard screen)
	'''counter_win = curses.newwin(1,2,10,10)

	for i in range(100):
		counter_win.clear()
		color = BLUE_YELLOW
		if i % 2 == 0:
			color = GREEN_YELLOW
		counter_win.addstr(f"Count: {i}", color)
		counter_win.refresh()
		time.sleep(0.1)'''

	#Pads (height, width)
	'''pad = curses.newpad(100,100)
	stdscr.refresh()
	for _ in range(100):
		for j in range(26):
			char = chr(67 + j)
			pad.addstr(char,BLUE_YELLOW)'''

	#Scroll horizontally through padded content
	'''for i in range(500):
		pad.refresh(0, i, 5, 5, 10, 25)
		time.sleep(0.1)'''
	#Move on screen
	'''for i in range(500):
		stdscr.clear()
		stdscr.refresh()
		pad.refresh(0, i, 5 + i, i, 10 + i, 25 + i)
		time.sleep(0.1)'''
	#Scroll vertically
	'''for i in range(500):
		pad.refresh(i, 0, 0, 0, 20, 20)
		time.sleep(0.5)'''
	
	#specify render window(left, top, str_row, str_col, end_row, end_col)
	'''pad.refresh(0,0,5,5,25,75)'''

	#get screen dimensions
	'''(curses.LINES -1, curses.COLS -1)'''

	#user input
	#poll user key
	while True:
		key = stdscr.getch()
		stdscr.addstr(5,5,f"Key: {key}")
		stdscr.refresh()

	#listen to key

	'''stdscr.nodelay(True)''' # stops getkey from delaying program, i.e its asynchronous

	'''x, y = 0, 0
	while True:
		try: #try block needed if nodelay is set to True
			key = stdscr.getkey()
		except:
			key = None
		if key == "KEY_B1":
			x -=1
		elif key == "KEY_B3":
			x +=1
		elif key == "KEY_A2":
			y -=1
		elif key == "KEY_C2":
			y +=1

		x = max(x,0)
		y = max(y,0)
		
		stdscr.clear()
		stdscr.addstr( y, x, "0")
		stdscr.refresh()'''

	'''#Textboxes & Rectangles
	win = curses.newwin(3,18,2,2)
	#Creating textbox in window
	box = Textbox(win, insert_mode = True)

	#displaying rectangle (needs to be drawn slightly outside)
	rectangle(stdscr, 1, 1, 5, 20)
	stdscr.refresh()

	#Allow user to edit box
	box.edit(TextBoxBehaviour)
	#get text inside box (.strip() removes trailing white spaces)
	text = box.gather().strip().replace("\n","")
	stdscr.addstr(10,40, text)
	#Text boxes not necessary, just a easier way to get text instead of using getch'''

	#Other functions
	#Switch attribute on until turned off
	'''stdscr.attron(BLUE_YELLOW)
	stdscr.attroff(BLUE_YELLOW)'''

	#screen borders
	'''stdscr.border()'''

	#move cursor
	'''stdscr.move(10,20)'''

	#display keystrokes
	'''curses.echo()'''

	'''while True:
		key = stdscr.getkey()
		if key == "q":
			break'''

	stdscr.getch()

#Inits curses passes object to main func
wrapper(main)
