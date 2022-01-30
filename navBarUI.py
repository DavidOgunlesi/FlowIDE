class Button():
    def __init__(self, name : str, action) -> None:
        self.name = name
        self.action = action

    def doAction(self) -> None:
        self.action(self.name)

class DropDownButton(Button):
    def __init__(self, name : str, action) -> None:
        self.dropdownItems = []
        super().__init__(name, action)

    def addItem(self, dropdown : Button)  -> None:
        self.dropdownItems.append(dropdown)

    def getDropdownItems(self) -> list[Button]:
        return self.dropdownItems

class NavBar():

    def __init__(self) -> None:
        self.items = []

    def addItem(self, button : Button, rect : tuple[int,int,int,int]) -> None:
        self.items.append((button, rect))#(t,l,b,r)

    def getItemFromPos(self,pos : tuple[int,int]) -> Button:
        (x,y) = pos
        for (button,(t,l,b,r)) in self.items:
            #if in rect
            if x <= r and x >= l and y >= t and y <= b:
                return button
        return None
