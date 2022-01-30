import curses
import time
from curses import wrapper
import util.inputHandler as input
import util.fileHandler as file
import re
from pygments import highlight
from pygments.lexers import PythonLexer
from util.formatters import TokenFormatter
import json
import traceback
TAB_SPACE = "   "

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

def renderLines(stdscr, lines, formatter, style, bgCol):
    for lineNum in range(0,len(lines)):
        line = " " + lines[lineNum]
        highlightedText = highlight(line, PythonLexer(), formatter)
        stringArrToParse = re.split(f'\[|\]', highlightedText)
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
                stdscr.addstr(lineNum, skip, el, curses.color_pair(col+1))
                skip += len(el)


def main(stdscr):
    bkgd = curses.COLOR_BLUE
    curses.init_pair(100, curses.COLOR_WHITE, curses.COLOR_BLUE)
    with open('styles/defualt.json', 'r') as f:
        style = json.load(f)

    curses.curs_set(2)
    curses.mousemask(1)
    #lines = ["\"hello\" + 'world' text!","asdasdasd","asdasdasd"]
    lines = file.readFileLines('main.py')
    stdscr.clear()
    stdscr.nodelay(True)
    debug_win = curses.newwin(1,50,0,70)
    formatter = TokenFormatter()
    pad = curses.newpad(1000,curses.COLS-1)
    stdscr.bkgd(' ', curses.color_pair(100))  
    pad.bkgd(' ', curses.color_pair(100))    
    debug_win.bkgd(' ', curses.color_pair(100))    
    scrolly = 0
    x, y = 0, 0
    while True:

        relY = y+scrolly
        try: #try block needed if nodelay is set to True
            key = stdscr.getch()
        except:
            key = None

        if key == curses.KEY_RESIZE:
            #curses.resizeterm(*stdscr.getmaxyx())
            print(curses.LINES-1, curses.COLS-1)
            stdscr.clear()
            stdscr.refresh()
            #pad.clear()
            #pad.refresh(scrolly, 1, 0, 0, curses.LINES-1, curses.COLS-1)
            continue
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
        elif key == input.DOWN:
            if y >= curses.LINES-1:
                scrolly+=1
            else:
                y +=1
        elif key == input.ENTER:
            lines, x, y, relY, scrolly = enter(lines, x, y, relY, scrolly)
        elif key == input.ESCAPE:
            #exit program
            break
        elif key == input.BACKSPACE:
            if x == 0 and y == 0:
                curses.beep()
            lines, x, y, relY = backspace(lines, x, y, relY)
        elif key >= 0 and key <= 256:
            lines, x, y, relY = defaultTextEntry(key, lines, x, y, relY)

        if y > len(lines)-1:
            curses.beep()
        #if y > curses.LINES-1:
            #scrolly -= y - curses.LINES-1
            #y = curses.LINES-1

        y = max(min(y, curses.LINES-1),0)
        maxLine = len(lines[min(len(lines), relY)])
        x = max(min(x, maxLine) ,0)
        #pad.erase()
        #pad.refresh(0, 0, 0, 0, curses.LINES-1, curses.COLS-1)
        renderLines(pad, lines, formatter, style, bkgd)
        #renderCursor
        pad.refresh(scrolly, 1, 0, 0, curses.LINES-1, curses.COLS-1)
        stdscr.move(y,x)
        debug_win.erase()
        debug_win.addstr(f"xy:[{x},{y}] scrolly: {scrolly} relY: {relY}", curses.color_pair(100))
        debug_win.refresh()
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