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
import lorem
import navBarUI as nav
from spellchecker import SpellChecker

TAB_SPACE = "   "
MAX_FILE_LENGTH = 10000
LINE_NUM_WIDTH = 7
LINE_NUM_PAD = 2
NAVIGATION_MENU_BAR_HEIGHT = 1
FILE_TAB_HEIGHT = 2
MENU_HEIGHT = NAVIGATION_MENU_BAR_HEIGHT + FILE_TAB_HEIGHT + 1
NAVIGATION_MENU_BUTTON_SPACING = 2
NAVIGATION_DROPDOWN_MENU_HEIGHT = 30

quit = False
spell = SpellChecker()

text_style_dict = {
    "Style.Default":  curses.A_NORMAL,
    "style.SpellingError": curses.A_UNDERLINE
    }


def countTabSpaces(string):
    i = 0
    spaceCount = 0
    tabCount = 0
    while i < len(string):
        c = string[i]
        if c == ' ':
            spaceCount += 1
        else:
            break
        if spaceCount >= len(TAB_SPACE):
            tabCount += 1
            spaceCount = 0
        i += 1
    return tabCount


def HandleInput(scr, key, lines, x, y, scrollx, scrolly, relX, relY, renderUpdate):
    global quit
    if key == curses.KEY_RESIZE:
        print(curses.LINES-1, curses.COLS-1)
        scr.clear()
        scr.refresh()

    if key == input.LEFT:
        x -= 1
        if x <= 0 and scrollx > 0:
            scrollx -= 1
            renderUpdate = True
    elif key == input.RIGHT:
        if x >= curses.COLS-1 - LINE_NUM_WIDTH:
            scrollx += 1
            renderUpdate = True
        else:
            x += 1
    elif key == input.UP:
        y -= 1
        if y > len(lines)-1:
            curses.beep()
        elif y <= 0 and scrolly > 0:
            scrolly -= 1
            renderUpdate = True
    elif key == input.DOWN:
        if y >= curses.LINES-1-MENU_HEIGHT:
            scrolly += 1
            renderUpdate = True
        else:
            y += 1
    elif key == input.ENTER:
        lines, x, y, relX, relY, scrolly = enter(lines, x, y, relX, relY, scrolly)
        renderUpdate = True
    elif key == input.ESCAPE:
        # exit program
        quit = True
    elif key == input.BACKSPACE:
        if x == 0 and y == 0:
            curses.beep()
        lines, x, y, relX, relY, scrolly = backspace(lines, x, y, relX, relY, scrolly)
        renderUpdate = True
    elif key == input.CTRL_C:
        lines, x, y, relX, relY, scrolly = copy(lines, x, y, relX, relY, scrolly)
        renderUpdate = True
    elif key == input.CTRL_V:
        lines, x, y, relX, relY, scrolly = paste(lines, x, y, relX, relY, scrolly)
        renderUpdate = True
    elif key >= 0 and key <= 256:
        lines, x, y, relX, relY = defaultTextEntry(key, lines, x, y, relX, relY)
        renderUpdate = True

    return lines, x, y, scrollx, scrolly, relX, relY, renderUpdate

def copy(lines, x, y, relX, relY, scrolly):
    pass


def paste(lines, x, y, relX, relY, scrolly):
    string = pyperclip.paste()
    pasteLines = string.replace('\r', '').replace('\t', TAB_SPACE).split('\n')
    #save text after paste location
    end = lines[relY][relX:]
    lines[relY] = lines[relY][:relX]
    
    for i in range(0,len(pasteLines)-1):
        enter(lines, x, y, relX, relY, scrolly)
    for i,line in enumerate(pasteLines):
        # Strip leading white space
        line = line.lstrip() 
        # Insert line
        lines[relY+i] = lines[relY+i][:relX] + line + lines[relY+i][relX:]
    # Move cursor
    y = relY+len(pasteLines)-1
    # Restore text after paste location
    lines[y] = lines[y] + end
    return lines, x, y, relX, relY, scrolly


def enter(lines, x, y, relX, relY, scrolly):
    # create new lines if needed
    lineRemainder = lines[relY][x:]
    lines.insert(relY, lines[relY][:x])
    x = 0
    # Indent if there is tab
    if (tabCount := countTabSpaces(lines[relY])) > 0:
        lines[relY+1] = TAB_SPACE * tabCount + lineRemainder
        x += len(TAB_SPACE) * tabCount
    else:
        lines[relY+1] = lineRemainder
    # if cursor is at bottom
    if y == curses.LINES-1-MENU_HEIGHT:
        scrolly += 1
    y += 1
    return lines, x, y, relX, relY, scrolly


def backspace(lines, x, y, relX, relY, scrolly):
    # if we are somewhere in the middle of a line
    relY = clamp(relY, 0, len(lines)-1)
    if x > 0:
        # If we have tab space on backspace, remove it entirely
        if lines[relY][x-len(TAB_SPACE):x] == TAB_SPACE:
            lines[relY] = lines[relY][:x-len(TAB_SPACE)] + lines[relY][x:]
            x -= len(TAB_SPACE)-1
        else:
            # delete text in place
            lines[relY] = lines[relY][:x-1] + lines[relY][x:]
        x -= 1
    # if at start of line
    elif relY > 0:
        # remove current line
        line = lines.pop(relY)
        relY -= 1
        # Place cursor at previous line
        x = len(lines[relY])
        # Append line to previous line
        lines[relY] += line
        y -= 1
        scrolly = max(scrolly - 1, 0)
    return lines, x, y, relX, relY, scrolly


def defaultTextEntry(key, lines, x, y, relX, relY):
    currStr = chr(key)
    if key == input.TAB:
        currStr = TAB_SPACE

    if currStr != "":
        if x >= len(lines[relY]):
            lines[relY] += currStr
        else:
            # none insert mode
            lines[relY] = lines[relY][:x] + currStr + lines[relY][x:]
        x += len(currStr)
    return lines, x, y, relX, relY


def renderLineNumbers(scr, color):
    for i in range(0, MAX_FILE_LENGTH):
        s = str(i).rjust(LINE_NUM_WIDTH-LINE_NUM_PAD, ' ')
        scr.addstr(i, 0, f'{s}|',  color)


def renderScrollBar(scr, scrolly, maxScrolly, color):
    scr.erase()
    i = int((scrolly/clamp(maxScrolly, 1, MAX_FILE_LENGTH))*curses.LINES-1)
    # i = clamp(i, 0, curses.LINES-2)
    barPercentage = (curses.LINES)/(curses.LINES+maxScrolly)
    barSizeFloat = barPercentage*curses.LINES
    barSize = max(int(barSizeFloat), 1)
    symbol = '-'
    if barSizeFloat >= 1:
        symbol = '???'
    elif barSizeFloat < 1 and barSizeFloat >= 0.5:
        symbol = '???'
    elif barSizeFloat < 0.5 and barSizeFloat >= 0.4:
        symbol = '???'
    elif barSizeFloat < 0.4 and barSizeFloat >= 0.3:
        symbol = '='
    elif barSizeFloat < 0.3:
        symbol = '-'

    top = clamp(i, 0, curses.LINES-barSize)
    bottom = top + barSize
    for y in range(top, bottom):
        scr.addstr(clamp(y, 0, curses.LINES - 2), 0, symbol, color)
    scr.refresh(0, 0, MENU_HEIGHT-1, curses.COLS-1,
                curses.LINES-1, curses.COLS - 1)


def renderLines(scr, lines, scrollx, scrolly, lexer, formatter, currHighlightStyle, bgCol):
    scr.clear()
    for lineNum in range(scrolly, min(len(lines), scrolly + curses.LINES)):
        line = lines[lineNum]
        #print(f"Before Format: {line}")
        if lexer is not None:
            highlightedText = highlight(line, lexer, formatter)
        else:
            highlightedText = line

        highlightedText = " " + highlightedText
        stringArrToParse = re.split(f'\[{formatter.hash}|{formatter.hash}\]',
                                    highlightedText)
        
        skip = 0
        col = 15
        # Highlight Syntax using style
        # [{self.hash}{self.hash}{ttype}|{style}{self.hash}]{value}
        styleAttr = curses.A_NORMAL
        for el in stringArrToParse:
            if el.startswith(f"{formatter.hash}Token"):
                data = el.split('|')
                token = data[0]
                style = data[1]
                styleAttr = text_style_dict[style]

                tokenArr = token.split('.')
                if 'Error' in tokenArr:
                    col = 12
                else:
                    for i in range(1, len(tokenArr)):
                        subTokens = tokenArr[i:]
                        currSearchKey = ""
                        for key in subTokens:
                            currSearchKey += f".{key}"
                            if currSearchKey in currHighlightStyle:
                                col = currHighlightStyle[currSearchKey]
                # Convert token to curses Color
                curses.init_pair(col+1, col, bgCol)
            else:
                scr.addstr(lineNum, clamp(skip, scrollx,
                           curses.COLS-LINE_NUM_WIDTH+scrollx), 
                           el, curses.color_pair(col+1) | styleAttr)
                skip += len(el)


def initNavMenu(nav_win, nav_bgcolor) -> nav.NavBar:
    # Set up navbar buttons
    fileBtn = nav.DropDownButton("File", ProcessNavActions)
    fileBtn.addItem(nav.Button("New File", ProcessNavActions))
    fileBtn.addItem(nav.Button("Open File", ProcessNavActions))
    fileBtn.addItem(nav.Button("Save", ProcessNavActions))
    fileBtn.addItem(nav.Button("Save As", ProcessNavActions))
    fileBtn.addItem(nav.Button("Save All", ProcessNavActions))
    fileBtn.addItem(nav.Button("Autosave", ProcessNavActions))
    fileBtn.addItem(nav.Button("Preferences", ProcessNavActions))

    editBtn = nav.DropDownButton("Edit", ProcessNavActions)
    selectionBtn = nav.DropDownButton("Selection", ProcessNavActions)
    viewBtn = nav.DropDownButton("View", ProcessNavActions)
    goBtn = nav.DropDownButton("Go", ProcessNavActions)
    runBtn = nav.DropDownButton("Run", ProcessNavActions)
    terminalBtn = nav.DropDownButton("Terminal", ProcessNavActions)
    helpBtn = nav.DropDownButton("Help", ProcessNavActions)
    navbar = createAndRenderNavgationBar(nav_win, NAVIGATION_MENU_BAR_HEIGHT, nav_bgcolor, 
                                         fileBtn, 
                                         editBtn,
                                         selectionBtn,
                                         viewBtn,
                                         goBtn,
                                         runBtn,
                                         terminalBtn,
                                         helpBtn)
    return navbar


def createAndRenderNavgationBar(scr, height, def_color, *menu_buttons):
    navbar = nav.NavBar()
    offset = 0
    for menu_btn in menu_buttons:
        text = menu_btn.name.center(len(menu_btn.name)+NAVIGATION_MENU_BUTTON_SPACING, ' ')
        width = min(curses.COLS-1//len(menu_buttons), len(text))  # +NAVIGATION_MENU_BUTTON_SPACING*2)
        scr.addstr(height//2, offset, text, def_color)
        navbar.addItem(menu_btn, (0, offset, height, offset + width))  # (t,l,b,r)
        offset += width
    return navbar


def renderNavgationBar(scr, navbar, def_color, spacing=2, selected_button=None, sel_attr=curses.A_REVERSE):
    scr.erase()
    for (button, (t, l, b, r)) in navbar.items:
        for i in range(t, b):
            text = button.name.center(len(button.name) + spacing, ' ')
            scr.addstr(i, l, text, def_color)
            if selected_button == button:
                scr.addstr(i, l, text, def_color | sel_attr)
    scr.refresh()


def renderDropDown(navbar, selectedButton, color):
    global MENU_HEIGHT
    subItems = selectedButton.getDropdownItems()
    (t, l, b, r) = navbar.getButtonRectFromName(selectedButton.name)
    # print(f"{NAVIGATION_DROPDOWN_MENU_HEIGHT}, {len(subItems)},{NAVIGATION_MENU_HEIGHT},{l}")#t+1+len(subItems)
    MENU_HEIGHT = NAVIGATION_MENU_BAR_HEIGHT + FILE_TAB_HEIGHT + len(subItems) + 1
    dpDwn_win = curses.newwin(len(subItems), curses.COLS-1, NAVIGATION_MENU_BAR_HEIGHT, 0)
    # dpDwn_win = curses.newwin(NAVIGATION_DROPDOWN_MENU_HEIGHT, len(subItems),NAVIGATION_MENU_HEIGHT,l)
    dpDwn_win.bkgd(' ', color)
    for i, subBtn in enumerate(subItems):
        dpDwn_win.addstr(t+i, l, subBtn.name, color) 
    dpDwn_win.refresh()
    # stdscr.clear()
    # renderNavgationBar(nav_win, navbar, color, selectedButton)
    return dpDwn_win


def CheckForButtonPress(nav_win, navbar, tab_bar, pos, sel_col):
    (x, y) = pos
    if (selectedButton := navbar.getItemFromPos((x, y))) is not None:
        nav_win.erase()
        renderNavgationBar(nav_win, navbar, sel_col, NAVIGATION_MENU_BUTTON_SPACING, selectedButton)
        # renderNavgationBar(nav_win, tab_bar, sel_col, NAVIGATION_MENU_BUTTON_SPACING, selectedButton)
        nav_win.refresh()
        if isinstance(selectedButton, nav.DropDownButton):
            renderDropDown(navbar, selectedButton, sel_col)


def ProcessNavActions(buttonName: str):
    pass


def main(stdscr):
    ########
    # Config
    ########
    bkgd = curses.COLOR_BLACK
    curses.init_pair(100, curses.COLOR_WHITE, curses.COLOR_BLACK)
    COL_DEFAULT = curses.color_pair(100)
    curses.init_pair(101, curses.COLOR_WHITE, 235)
    COL_OFFDARK = curses.color_pair(101)
    curses.init_pair(102, 245, curses.COLOR_BLACK)
    COL_DIMTEXT = curses.color_pair(102)
    curses.init_pair(103, curses.COLOR_WHITE, 240)
    COL_GRAY = curses.color_pair(103)
    # Load style
    with open('styles/defualt.json', 'r') as f:
        currHighlightStyle = json.load(f)

    curses.curs_set(2)
    curses.mousemask(-1)
    stdscr.clear()
    stdscr.nodelay(True)
    stdscr.bkgd(' ', COL_DEFAULT)  

    # Line number display
    line_num_pad = curses.newpad(MAX_FILE_LENGTH, LINE_NUM_WIDTH)
    line_num_pad.bkgd(' ', COL_DIMTEXT)
    renderLineNumbers(line_num_pad,  COL_DIMTEXT)

    # Main editable text content pad
    content_display_pad = curses.newpad(MAX_FILE_LENGTH, curses.COLS-1)
    content_display_pad.bkgd(' ', COL_DEFAULT)   

    # Scroll bar window
    scroll_display_pad = curses.newpad(curses.LINES, 4) 
    scroll_display_pad.bkgd(' ', COL_OFFDARK)

    # Navigation Window
    nav_pad = curses.newpad(NAVIGATION_MENU_BAR_HEIGHT, curses.COLS+5) 
    nav_pad.bkgd(' ', COL_OFFDARK)

    navbar = initNavMenu(nav_pad, COL_OFFDARK)

    # Tab Window
    tab_pad = curses.newpad(FILE_TAB_HEIGHT, curses.COLS+5) 
    tab_pad.bkgd(' ', COL_DEFAULT)
    # Tabs
    file_tab_btn = nav.Button("file1.txt", ProcessNavActions)
    tab_bar = createAndRenderNavgationBar(tab_pad, FILE_TAB_HEIGHT, COL_GRAY, file_tab_btn)

    # Debug Window
    debug_win = curses.newwin(1, 50, 0, 70) 
    debug_win.bkgd(' ', COL_DEFAULT)  

    # Load File and Init formatter with Lexer
    # filePath ='testfiles/LongPythonProgram.py'#'main.py'
    file_path = 'testfiles/python copy.py'
    if file.fileExists(file_path):
        lines = file.readFileLines(file_path)
        lexer = guess_lexer_for_filename(file_path, '\n'.join(lines))
    else:
        lorem_text = ""
        for _ in range(0, 0):
            lorem_text += lorem.paragraph() + "\n"
        lines = lorem_text.split('\n')
        lexer = None
    formatter = TokenFormatter()

    #################
    # Main Render Loop
    #################
    scrollx, scrolly = 0, 0
    x, y = 0, 0
    renderUpdate = True
    while not quit:
        relY = y+scrolly
        relX = x+scrollx
        # Key Inputs
        try: 
            key = stdscr.getch()
        except:
            key = None

        lines, x, y,scrollx,scrolly,relX, relY,renderUpdate = HandleInput(stdscr, key, lines,x, y, scrollx, scrolly,relX, relY, renderUpdate)
        
        # Mouse Input
        if key == input.MOUSE:
            _, xx, yy, _, context = curses.getmouse()
            if context == input.MOUSE_LEFT_CLICK or context == input.MOUSE_LEFT_PRESSED:
                CheckForButtonPress(nav_pad, navbar, tab_bar, (xx, yy), COL_OFFDARK)
                x = xx - LINE_NUM_WIDTH
                y = yy - MENU_HEIGHT
            elif context == input.MOUSE_SCROLL_DOWN:
                scrolly += 1
                renderUpdate = True
            elif context == input.MOUSE_SCROLL_UP:
                scrolly -= 1
                renderUpdate = True
        
        scrolly = clamp(scrolly, 0, MAX_FILE_LENGTH)
        if y > len(lines)-1:
            curses.beep()

        y = clamp(y, 0, min(curses.LINES - 1, len(lines)-1-scrolly))
        maxLine = len(lines[min(len(lines)-1, relY)])
        x = clamp(x, 0, maxLine-scrollx)

        # Render only when we need to
        if renderUpdate:
            renderLines(content_display_pad, lines, scrollx, scrolly, lexer, formatter, currHighlightStyle, bkgd)
            renderScrollBar(scroll_display_pad, scrolly, max(0, len(lines) - 1 - curses.LINES), COL_OFFDARK)
        renderUpdate = False

        content_display_pad.refresh(scrolly, scrollx + 1, MENU_HEIGHT, LINE_NUM_WIDTH, curses.LINES-1, curses.COLS-3)
        line_num_pad.refresh(scrolly, 0, MENU_HEIGHT, 0, curses.LINES-1, LINE_NUM_WIDTH)
        nav_pad.refresh(0,0,0,0,NAVIGATION_MENU_BAR_HEIGHT+1, curses.COLS-1)
        tab_pad.refresh(0, 0, MENU_HEIGHT-NAVIGATION_MENU_BAR_HEIGHT-2, 0, MENU_HEIGHT-NAVIGATION_MENU_BAR_HEIGHT+FILE_TAB_HEIGHT-1, curses.COLS-1)
        
        #render cursor off pad bounds
        content_display_pad.move(MAX_FILE_LENGTH-10,0)
        line_num_pad.move(MAX_FILE_LENGTH-10,0)
        nav_pad.move(0,curses.COLS+4)
        tab_pad.move(0,curses.COLS+4)
        scroll_display_pad.move(0,3)
        
        #render main cursor on screen
        stdscr.move(min(curses.LINES-1, y+MENU_HEIGHT), min(curses.COLS-1, x + LINE_NUM_WIDTH))
        #debug_win.erase()
        #debug_win.addstr(f"xy:[{x},{y}] scrollxy: {scrollx},{scrolly} relY: {relY}", curses.color_pair(100))
        #debug_win.refresh()
        # yEnd = clamp(len(lines)-scrolly, 0, MAX_FILE_LENGTH-scrolly)+1
    # stdscr.getch()


if __name__ == '__main__':
    file.ensure_dir("testfiles/")
    try:
        wrapper(main)
    except:
        tb = traceback.format_exc()
        crash = str(tb)
        print(crash)
        timeX = str(time.time())
        file.ensure_dir("crashlogs/")
        with open("crashlogs/CRASH-"+timeX+".txt", "w") as crashLog:
            for i in crash:
                i = str(i)
                crashLog.write(i)

# for match in re.finditer('"[^"]*"|\'[^\']*\'', line, re.S):
    # (start, end) = match.span()
    # stdscr.addstr(lineNum, start, lines[lineNum][start:end],STRING)