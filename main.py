import os, screeninfo
import pygame
from pygame.locals import *

import game.manager

monitor = screeninfo.get_monitors()[0]
SCREENRECT = Rect(0, 0, monitor.width, monitor.height)


class App():
    def __init__(self):
        self.manager = game.manager.Manager(SCREENRECT)

    def run(self):
        self.manager.run()


if __name__ == '__main__':
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    app = App()
    app.run()
