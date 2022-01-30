import curses
import time
from curses import wrapper
import util.inputHandler as input
import util.fileHandler as file
from util.math import clamp
import re
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from util.formatters import TokenFormatter
import json
import traceback
import pyperclip
TAB_SPACE = "   "
MAX_FILE_LENGTH = 10000
LINE_NUM_WIDTH = 7
LINE_NUM_PAD = 2
quit = False


def countTabSpaces(string):
    i = 0
    spaceCount = 0
    tabCount = 0
    while i < len(string):
        c = string[i]
        if c == ' ':
            spaceCount+=1
        else:
            break;
        if spaceCount >= len(TAB_SPACE):
            tabCount += 1
            spaceCount = 0
        i+=1
    return tabCount

def HandleInput(scr, key, lines, x, y, scrolly, relY, renderUpdate):
    global quit
    if key == curses.KEY_RESIZE:
        print(curses.LINES-1, curses.COLS-1)
        scr.clear()
        scr.refresh()
        #pad.clear()
        #pad.refresh(scrolly, 1, 0, 0, curses.LINES-1, curses.COLS-1)

    if key == input.MOUSE:
        _, x, y, _, _ = curses.getmouse()
        maxLine = len(lines[min(len(lines), relY)])
        x = max(min(x, maxLine) ,0)

    if key == input.LEFT:
        x -=1
    elif key == input.RIGHT:
        x +=1
    elif key == input.UP:
        y -=1
        if y > len(lines)-1:
            curses.beep()
        elif y <= 0 and scrolly > 0:
            scrolly-=1
            renderUpdate = True
    elif key == input.DOWN:
        if y >= curses.LINES-1:
            scrolly+=1
            renderUpdate = True
        else:
            y +=1
    elif key == input.ENTER:
        lines, x, y, relY, scrolly = enter(lines, x, y, relY, scrolly)
        renderUpdate = True
    elif key == input.ESCAPE:
        #exit program
        quit = True
    elif key == input.BACKSPACE:
        if x == 0 and y == 0:
            curses.beep()
        lines, x, y, relY = backspace(lines, x, y, relY)
        renderUpdate = True
    elif key >= 0 and key <= 256:
        lines, x, y, relY = defaultTextEntry(key, lines, x, y, relY)
        renderUpdate = True

    return lines, x, y, scrolly, relY, renderUpdate

def enter(lines,x, y, relY, scrolly):
    #create new lines if needed
    lineRemainder = lines[relY][x:] 
    lines.insert(relY,lines[relY][:x])
    x = 0
    #Indent if there is tab
    if (tabCount := countTabSpaces(lines[relY])) > 0:
        lines[relY+1] = TAB_SPACE * tabCount  + lineRemainder
        x += len(TAB_SPACE) * tabCount
    else:
        lines[relY+1] = lineRemainder
    #if cursor is at bottom
    if y == curses.LINES-1:
        scrolly += 1
    y+=1
    return lines, x, y, relY, scrolly

def backspace(lines,x, y, relY):
    #if we are somewhere in the middle of a line
    if x > 0:
        #If we have tab space on backspace, remove it entirely
        if lines[relY][x-len(TAB_SPACE):x] == TAB_SPACE:
            lines[relY] = lines[relY][:x-len(TAB_SPACE)] + lines[relY][x:]
            x -= len(TAB_SPACE)-1
        else:
            #delete text in place
            lines[relY] = lines[relY][:x-1] + lines[relY][x:]
        x -= 1
    #if at start of line
    elif relY > 0:
        #remove current line
        line = lines.pop(relY)
        relY-=1
        #Place cursor at previous line
        x = len(lines[relY])
        #Append line to previous line
        lines[relY] += line
        y-=1
    return lines, x, y, relY

def defaultTextEntry(key,lines,x, y, relY):
    currStr = chr(key)
    if key == input.TAB:
        currStr = TAB_SPACE

    if currStr != "":
        if x >= len(lines[relY]):
            lines[relY] += currStr
        else:
            #none insert mode
            lines[relY] = lines[relY][:x] + currStr + lines[relY][x:]
        x += len(currStr)
    return lines, x, y, relY

def renderLineNumbers(scr, color):
    for i in range(0,MAX_FILE_LENGTH):
        s = str(i).rjust(LINE_NUM_WIDTH-LINE_NUM_PAD, ' ')
        scr.addstr(i, 0, f'{s}|',  color)

def renderScrollBar(scr, scrolly, maxScrolly, color):
    scr.erase()
    i = int((scrolly/maxScrolly)*curses.LINES-1)
    i = clamp(i, 0, curses.LINES-2)
    scr.addstr(i, 0, '█', color)
    scr.refresh()

def renderLines(scr, lines, scrolly, lexer, formatter, style, bgCol):
    for lineNum in range(scrolly,min(len(lines) ,scrolly + curses.LINES)):
        line = " " + lines[lineNum]
        highlightedText = highlight(line, lexer, formatter)
        stringArrToParse = re.split(f'\[{formatter.hash}|{formatter.hash}\]', highlightedText)
        skip = 0
        col = 15
        #Highlight Syntax using style
        for el in stringArrToParse:
            if el.startswith(f"{formatter.hash}Token"):
                tokenArr = el.split('.')
                for i in range(1,len(tokenArr)):
                    subTokens = el.split('.')[i:]
                    currSearchKey = ""
                    for key in subTokens:
                        currSearchKey += f".{key}"
                        if currSearchKey in style:
                            col = style[currSearchKey]
                #Convert token to curses Color
                curses.init_pair(col+1, col, bgCol)
            else:
                scr.addstr(lineNum, skip, el, curses.color_pair(col+1))
                skip += len(el)


def main(stdscr):
    ########
    #Config
    ########
    bkgd = curses.COLOR_BLACK
    curses.init_pair(100, curses.COLOR_WHITE, curses.COLOR_BLACK)
    COL_DEFAULT = curses.color_pair(100)
    curses.init_pair(101, curses.COLOR_WHITE, 235)
    COL_OFFDARK = curses.color_pair(101)
    curses.init_pair(102,245, curses.COLOR_BLACK)
    COL_DIMTEXT = curses.color_pair(102)
    #Load style
    with open('styles/defualt.json', 'r') as f:
        style = json.load(f)

    curses.curs_set(2)
    curses.mousemask(1)
    stdscr.clear()
    stdscr.nodelay(True)
    stdscr.bkgd(' ', COL_DEFAULT)  

    #Line number display
    line_num_pad = curses.newpad(MAX_FILE_LENGTH, LINE_NUM_WIDTH)
    line_num_pad.bkgd(' ', COL_DIMTEXT)
    renderLineNumbers(line_num_pad,  COL_DIMTEXT)

    #Main editable text content pad
    content_display_pad = curses.newpad(MAX_FILE_LENGTH,curses.COLS-1)
    content_display_pad.bkgd(' ', COL_DEFAULT)   

    #Scroll bar window
    scroll_display_win = curses.newwin(curses.LINES,1,0,curses.COLS-1) 
    scroll_display_win.bkgd(' ', COL_OFFDARK)

    #Debug Window
    debug_win = curses.newwin(1,50,0,70) 
    debug_win.bkgd(' ', COL_DEFAULT)  

    #Load File and Init formatter with Lexer
    filePath = 'main.py'
    lines = file.readFileLines(filePath)
    lexer = guess_lexer_for_filename(filePath, '\n'.join(lines))
    formatter = TokenFormatter()
    #################
    #Main Render Loop
    #################
    scrolly = 0
    x, y = 0, 0
    renderUpdate = True
    while not quit:
        relY = y+scrolly

        #Key Inputs
        try: 
            key = stdscr.getch()
        except:
            key = None

        lines, x, y, scrolly, relY, renderUpdate = HandleInput(stdscr, key, lines, x, y, scrolly, relY, renderUpdate)

        if y > len(lines)-1:
            curses.beep()

        y = max(min(y, min(curses.LINES-1,len(lines)-1-scrolly)),0)
        maxLine = len(lines[min(len(lines)-1, relY)])
        x = max(min(x, maxLine) ,0)

        #Render only when we need to
        if renderUpdate:
            renderLines(content_display_pad, lines,scrolly, lexer, formatter, style, bkgd)
            renderScrollBar(scroll_display_win, relY, len(lines)-1, COL_OFFDARK)
        renderUpdate = False

        #renderCursor
        stdscr.move(y,x+LINE_NUM_WIDTH)

        content_display_pad.refresh(scrolly, 1, 0, LINE_NUM_WIDTH, curses.LINES-1, curses.COLS-3)
        line_num_pad.refresh(scrolly, 0, 0, 0, max(0,min(curses.LINES-1,len(lines)-scrolly)), LINE_NUM_WIDTH)
        
        #debug_win.erase()
        #debug_win.addstr(f"xy:[{x},{y}] scrolly: {scrolly} relY: {relY}", curses.color_pair(100))
        #debug_win.refresh()
    #stdscr.getch()


if __name__ == '__main__':
    try:
      wrapper(main)
    except Exception as e:
        tb = traceback.format_exc()
        crash = str(tb)
        print(crash)
        timeX=str(time.time())
        with open("crashlogs/CRASH-"+timeX+".txt","w") as crashLog:
            for i in crash:
                i=str(i)
                crashLog.write(i)

#for match in re.finditer('"[^"]*"|\'[^\']*\'', line, re.S):
    #(start, end) = match.span()
    #stdscr.addstr(lineNum, start, lines[lineNum][start:end],STRING)