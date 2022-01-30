import curses
import time
from curses import wrapper
from curses.textpad import rectangle
from turtle import goto
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
import navBarUI as nav
TAB_SPACE = "   "
MAX_FILE_LENGTH = 10000
LINE_NUM_WIDTH = 7
LINE_NUM_PAD = 2
NAVIGATION_MENU_HEIGHT = 2
NAVIGATION_MENU_BUTTON_SPACING = 2
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

def HandleInput(scr, key, lines, x, y, scrollx, scrolly, relX, relY, renderUpdate):
    global quit
    if key == curses.KEY_RESIZE:
        print(curses.LINES-1, curses.COLS-1)
        scr.clear()
        scr.refresh()
        #pad.clear()
        #pad.refresh(scrolly, 1, 0, 0, curses.LINES-1, curses.COLS-1)

    if key == input.LEFT:
        x -=1
        if x <= 0 and scrollx > 0:
            scrollx-=1
            renderUpdate = True
    elif key == input.RIGHT:
        if x >= curses.COLS-1 - LINE_NUM_WIDTH:
            scrollx+=1
            renderUpdate = True
        else:
            x +=1
    elif key == input.UP:
        y -=1
        if y > len(lines)-1:
            curses.beep()
        elif y <= 0 and scrolly > 0:
            scrolly-=1
            renderUpdate = True
    elif key == input.DOWN:
        if y >= curses.LINES-1-NAVIGATION_MENU_HEIGHT:
            scrolly+=1
            renderUpdate = True
        else:
            y +=1
    elif key == input.ENTER:
        lines, x, y, relX, relY, scrolly = enter(lines, x, y, relX, relY, scrolly)
        renderUpdate = True
    elif key == input.ESCAPE:
        #exit program
        quit = True
    elif key == input.BACKSPACE:
        if x == 0 and y == 0:
            curses.beep()
        lines, x, y, relX, relY = backspace(lines, x, y,relX, relY)
        renderUpdate = True
    elif key >= 0 and key <= 256:
        lines, x, y, relX, relY = defaultTextEntry(key, lines, x, y, relX, relY)
        renderUpdate = True

    return lines, x, y, scrollx, scrolly, relX, relY, renderUpdate

def enter(lines,x, y, relX, relY, scrolly):
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
    if y == curses.LINES-1-NAVIGATION_MENU_HEIGHT:
        scrolly += 1
    y+=1
    return lines, x, y, relX, relY, scrolly

def backspace(lines,x, y, relX, relY):
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
    return lines, x, y, relX, relY

def defaultTextEntry(key,lines,x, y, relX, relY):
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
    return lines, x, y, relX, relY

def renderLineNumbers(scr, color):
    for i in range(0,MAX_FILE_LENGTH):
        s = str(i).rjust(LINE_NUM_WIDTH-LINE_NUM_PAD, ' ')
        scr.addstr(i, 0, f'{s}|',  color)

def renderScrollBar(scr, scrolly, maxScrolly, color):
    scr.erase()
    i = int((scrolly/maxScrolly)*curses.LINES-1)
    #i = clamp(i, 0, curses.LINES-2)
    barSize  = int((curses.LINES*curses.LINES)/(curses.LINES+maxScrolly))
    #barSize = int(barPercentSize*curses.LINES)
    for y in range(0,barSize):
        scr.addstr(clamp(i+y, 0, curses.LINES-2), 0, '█', color)
    scr.refresh(0,0,NAVIGATION_MENU_HEIGHT-1,curses.COLS-1,curses.LINES-1,curses.COLS-1)

def renderLines(scr, lines, scrollx, scrolly, lexer, formatter, style, bgCol):
    for lineNum in range(scrolly,min(len(lines) ,scrolly + curses.LINES )):
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
                scr.addstr(lineNum,clamp(skip, scrollx,curses.COLS-LINE_NUM_WIDTH+scrollx), el, curses.color_pair(col+1))
                skip += len(el)

def createAndRenderNavgationBar(scr, def_color, *menu_buttons):
    navbar = nav.NavBar()
    offset = 0
    for menu_btn in menu_buttons:
        text = menu_btn.name.center(len(menu_btn.name)+NAVIGATION_MENU_BUTTON_SPACING, ' ')
        width = min(curses.COLS-1//len(menu_buttons),len(text))#+NAVIGATION_MENU_BUTTON_SPACING*2)
        scr.addstr(0, offset , text, def_color)
        navbar.addItem(menu_btn,(0,offset,NAVIGATION_MENU_HEIGHT-1,offset+width))#(t,l,b,r)
        offset += width
    return navbar

def renderNavgationBar(scr, navbar, def_color, selected_button = None, sel_attr = curses.A_REVERSE):
    scr.erase()
    for (button,(t,l,b,r)) in navbar.items:
        for i in range(t, b):
            text = button.name.center(len(button.name) + NAVIGATION_MENU_BUTTON_SPACING, ' ')
            scr.addstr(i, l, text, def_color)
            if selected_button == button:
                scr.addstr(i, l, text, def_color | sel_attr)
    scr.refresh()

def ProcessNavActions(buttonName : str):
    pass


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
    scroll_display_win = curses.newpad(curses.LINES,1) 
    scroll_display_win.bkgd(' ', COL_OFFDARK)

    #Navigation Window
    nav_win = curses.newwin(NAVIGATION_MENU_HEIGHT-1, curses.COLS,0,0) 
    nav_win.bkgd(' ', COL_OFFDARK)
    
    #Set up navbar buttons
    fileBtn = nav.DropDownButton("File", ProcessNavActions)
    editBtn = nav.DropDownButton("Edit", ProcessNavActions)
    selectionBtn = nav.DropDownButton("Selection", ProcessNavActions)
    viewBtn = nav.DropDownButton("View", ProcessNavActions)
    goBtn = nav.DropDownButton("Go", ProcessNavActions)
    runBtn = nav.DropDownButton("Run", ProcessNavActions)
    terminalBtn = nav.DropDownButton("Terminal", ProcessNavActions)
    helpBtn = nav.DropDownButton("Help", ProcessNavActions)
    navbar = createAndRenderNavgationBar(nav_win,COL_OFFDARK, fileBtn,editBtn,selectionBtn,viewBtn,goBtn,runBtn,terminalBtn,helpBtn)
    
    #renderNavgationBar(nav_win, ["File", "Edit", "Selection", "View", "Go", "Run", "Terminal", "Help"], COL_OFFDARK)

    #Debug Window
    debug_win = curses.newwin(1,50,0,70) 
    debug_win.bkgd(' ', COL_DEFAULT)  

    #Load File and Init formatter with Lexer
    #filePath ='testfiles/LongPythonProgram.py'#'main.py'
    filePath ='testfiles/CProgram.c'
    lines = file.readFileLines(filePath)
    lexer = guess_lexer_for_filename(filePath, '\n'.join(lines))
    formatter = TokenFormatter()
    #################
    #Main Render Loop
    #################
    scrollx, scrolly = 0, 0
    x, y = 0, 0
    renderUpdate = True
    while not quit:
        relY = y+scrolly
        relX = x+scrollx
        #Key Inputs
        try: 
            key = stdscr.getch()
        except:
            key = None

        lines, x, y, scrollx, scrolly, relX, relY, renderUpdate = HandleInput(stdscr, key, lines, x, y, scrollx, scrolly,relX, relY, renderUpdate)

        if key == input.MOUSE:
            _, x, y, _, _ = curses.getmouse()
            if (selectedButton := navbar.getItemFromPos((x, y))) != None:
                print(selectedButton.name + "\n")
                renderNavgationBar(nav_win, navbar, COL_OFFDARK, selectedButton)
            x -= LINE_NUM_WIDTH
            y -= NAVIGATION_MENU_HEIGHT


        if y > len(lines)-1:
            curses.beep()

        #y = max(min(y, min(curses.LINES-1,len(lines)-1-scrolly)),0)
        y = clamp(y,0, min(curses.LINES-1,len(lines)-1-scrolly))
        maxLine = len(lines[min(len(lines)-1, relY)])
        x = clamp(x,0, maxLine-scrollx) #max(min(x, maxLine) ,0)

        #Render only when we need to
        if renderUpdate:
            renderLines(content_display_pad, lines, scrollx, scrolly, lexer, formatter, style, bkgd)
            renderScrollBar(scroll_display_win, relY, len(lines)-1, COL_OFFDARK)
        renderUpdate = False
        #renderNavgationBar(nav_win, ["File", "Edit", "Selection", "View", "Go", "Run", "Terminal", "Help"], COL_OFFDARK)

        #renderCursor
        #print(f"{curses.LINES-1} {curses.COLS-1} { y+NAVIGATION_MENU_HEIGHT} {x+LINE_NUM_WIDTH}")

        content_display_pad.refresh(scrolly,scrollx + 1, NAVIGATION_MENU_HEIGHT, LINE_NUM_WIDTH, curses.LINES-1, curses.COLS-3)
        line_num_pad.refresh(scrolly, 0, NAVIGATION_MENU_HEIGHT, 0, max(0,min(curses.LINES-1,len(lines)-scrolly)), LINE_NUM_WIDTH)
        nav_win.refresh()

        stdscr.move(min(curses.LINES-1,y+NAVIGATION_MENU_HEIGHT),min(curses.COLS-1,x+LINE_NUM_WIDTH))
        #debug_win.erase()
        #debug_win.addstr(f"xy:[{x},{y}] scrollxy: {scrollx},{scrolly} relY: {relY}", curses.color_pair(100))
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