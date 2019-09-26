import pygame

screensize = 1024, 600
appres = 256, 150
zoom = screensize[0] / appres[0], screensize[1] / appres[1]

CHANGECOLOR = pygame.USEREVENT + 1


class PicoPalette(dict):
    '''dict containing color palette based on pico8 palette + colorkey'''

    def __init__(self):
        self.colorlist = []

        dict.__init__(self, {
            "BLACK": (0, 0, 0),
            "DARKBLUE": (29, 43, 83),
            "DARKPURPLE": (126, 37, 83),
            "DARKGREEN": (0, 135, 81),
            "BROWN": (171, 82, 54),
            "DARKGRAY": (95, 87, 79),
            "LIGHTGRAY": (194, 195, 199),
            "WHITE": (255, 241, 232),
            "RED": (255, 0, 77),
            "ORANGE": (255, 163, 0),
            "YELLOW": (255, 236, 39),
            "GREEN": (0, 228, 54),
            "BLUE": (41, 173, 255),
            "INDIGO": (131, 118, 156),
            "PINK": (255, 119, 168),
            "PEACH": (255, 204, 170),
            "COLORKEY": (255, 255, 0)
        })

        for color in self.values():
            self.colorlist.append(color)

    def __getattr__(self, item):
        # make value in the dictionnary accessible just by key names
        return self[item]

    def getcolornum(self, num):
        return self.colorlist[num]


class Paper(pygame.Surface):
    '''Surface on which drawing are done'''

    def __init__(self, bgcolor):
        # Create a surface with parameter bgcolor
        pygame.Surface.__init__(self, size=appres)
        self.bgcolor = bgcolor
        self.clear()

    def clear(self):
        # clear the Paper
        self.fill(self.bgcolor)


class Interface(pygame.Surface):
    '''Surface on which interface is drawn'''

    def __init__(self):
        pygame.Surface.__init__(self, size=appres)

        self.palette = PicoPalette()
        self.buttonset = ButtonSet()

        self.set_colorkey(self.palette.COLORKEY)
        self.fill(self.palette.COLORKEY)

        for p, col in enumerate(self.palette.values()):
            pygame.draw.rect(self, col, pygame.Rect(
                p * appres[0] / 16, 0, appres[0] / 16, 8))
            self.buttonset.addbutton(
                Button((p * appres[0] / 16, 0), (appres[0] / 16, 8), str(p))
            )

        pygame.draw.rect(self, (0, 0, 0), pygame.Rect(0, 8, appres[0], 1))


class ButtonSet(dict):
    ''' a set of buttons '''

    def __init__(self):
        dict.__init__({})

    def addbutton(self, button):
        self[button.label] = button

    def handleclick(self, clickpos):
        # wo go through all buttons to know if one is clicked then if it does
        # we launch on_click method of button
        for butlabel, button in self.items():
            if button.collidepoint(clickpos):
                button.on_click()

# TODO : button subclasses


class Button(pygame.Rect):
    ''' a base class for a button '''

    def __init__(self, pos, size, label):
        self.label = label
        rect = pygame.Rect(pos, size)
        pygame.Rect.__init__(self, rect)

    def on_click(self):
        # on click action, should be overriden
        pygame.event.post(pygame.event.Event(
            CHANGECOLOR, colornum=int(self.label)))


def on_cleanup():
    pygame.quit()


class SpouiPaint:
    ''' Drawing app main class '''

    def __init__(self):
        self._running = True
        self._display_surf = None
        self.interface = Interface()
        self.palette = PicoPalette()
        self.paper = Paper(self.palette.WHITE)
        self.size = self.width, self.height = screensize
        self.mousepos = 0, 0
        self.prevmousepos = 0, 0
        self.mouseclicked = 0
        self.currentcolor = self.palette.BLACK

    def on_init(self):
        self._running = True
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.mouseclicked = True
            self.interface.buttonset.handleclick(self.mousepos)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.mouseclicked = 0
        elif event.type == CHANGECOLOR:
            self.currentcolor = self.palette.getcolornum(event.colornum)

    def on_loop(self):
        self.prevmousepos = self.mousepos
        self.mousepos = pygame.mouse.get_pos()
        self.mousepos = self.mousepos[0] / zoom[0], self.mousepos[1] / zoom[1]
        self.mouseclicked = pygame.mouse.get_pressed()[0]

    def on_render(self):
        if self.mouseclicked == 1:
            pygame.draw.line(self.paper, self.currentcolor,
                             self.prevmousepos, self.mousepos, 1)

        self._display_surf.blit(pygame.transform.scale(
            self.paper, screensize), (0, 0))
        self._display_surf.blit(pygame.transform.scale(
            self.interface, screensize), (0, 0))
        pygame.display.flip()

    def on_execute(self):
        self.on_init()

        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        on_cleanup()


if __name__ == '__main__':
    spouipaint = SpouiPaint()
    spouipaint.on_execute()
