import curses
import time
from curses import wrapper
#from curses.textpad import Textbox, rectangle
import util.inputHandler as input
import re

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

def enter(lines,x,y):
    #create new lines if needed
    lineRemainder = lines[y][x:] 
    lines.insert(y,lines[y][:x])
    x = 0
    #Indent if there is tab
    if (tabCount := countTabSpaces(lines[y])) > 0:
        lines[y+1] = TAB_SPACE * tabCount  + lineRemainder
        x += len(TAB_SPACE) * tabCount
    else:
        lines[y+1] = lineRemainder
    y +=1
    return lines, x, y

def backspace(lines,x,y):
    #if we are somewhere in the middle of a line
    if x > 0:
        #If we have tab space on backspace, remove it entirely
        if countTabSpaces(lines[y]) > 0:
            lines[y] = lines[y][:x-len(TAB_SPACE)] + lines[y][x:]
            x -= len(TAB_SPACE)-1
        else:
            #delete text in place
            lines[y] = lines[y][:x-1] + lines[y][x:]
        x -= 1
    #if at start of line
    elif y > 0:
        #remove current line
        line = lines.pop(y)
        y-=1
        #Place cursor at previous line
        x = len(lines[y])
        #Append line to previous line
        lines[y] += line
    return lines, x, y

def defaultTextEntry(key,lines,x,y):
    currStr = chr(key)
    if key == input.TAB:
        currStr = TAB_SPACE

    if currStr != "":
        if x >= len(lines[y]):
            lines[y] += currStr
        else:
            #none insert mode
            lines[y] = lines[y][:x] + currStr + lines[y][x:]
        x += len(currStr)
    return lines, x, y

def main(stdscr):
    curses.curs_set(2)
    #curses.beep()

    lines = ["\"hello\" + 'world'","asdasdasd","asdasdasd"]
    stdscr.clear()
    stdscr.nodelay(True)
    #curses.echo()
    x, y = 0, 0
    while True:
        currStr = ""
        try: #try block needed if nodelay is set to True
            key = stdscr.getch()
        except:
            key = None

        if key == input.LEFT:
            x -=1
        elif key == input.RIGHT:
            x +=1
        elif key == input.UP:
            y -=1
        elif key == input.DOWN:
            y +=1
        elif key == input.ENTER:
            lines, x, y = enter(lines, x, y)
        elif key == input.ESCAPE:
            #exit program
            break
        elif key == input.BACKSPACE:
            if x == 0 and y == 0:
                curses.beep()
            lines, x, y = backspace(lines, x, y)
        elif key >= 0 and key <= 256:
            lines, x, y = defaultTextEntry(key, lines, x, y)

        if y > len(lines)-1:
            curses.beep()

        y = max(min(y,len(lines)-1),0)
        x = max(min(x,len(lines[y])) ,0)
        stdscr.clear()

        for lineNum in range(0,len(lines)):
            line = lines[lineNum]
            stdscr.addstr(lineNum, 0, lines[lineNum])

            curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
            STRING = curses.color_pair(1)

            for match in re.finditer('"[^"]*"|\'[^\']*\'', line, re.S):
                (start, end) = match.span()
                stdscr.addstr(lineNum, start, lines[lineNum][start:end],STRING)

        stdscr.move(y,x)
        stdscr.refresh()
    stdscr.getch()


if __name__ == '__main__':
    wrapper(main)