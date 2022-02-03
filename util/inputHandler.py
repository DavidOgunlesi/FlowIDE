
from tkinter import LEFT
import curses

ESCAPE = 27
UP = 259
DOWN = 258
LEFT = 260
RIGHT = 261
ENTER = 10
BACKSPACE = 8
CTRL_C = 3
CTRL_V = 22
TAB = 9
MOUSE = 539
MOUSE_LEFT_CLICK = curses.BUTTON1_CLICKED
MOUSE_LEFT_PRESSED = curses.BUTTON1_PRESSED
MOUSE_RIGHT_CLICK = curses.BUTTON3_CLICKED
MOUSE_RIGHT_PRESSED = curses.BUTTON3_PRESSED
MOUSE_SCROLL_UP = curses.BUTTON4_PRESSED
MOUSE_SCROLL_DOWN = 2097152 # magic number :(