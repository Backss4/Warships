import platform
import pygame
import pygame_gui
from game import menu, game
from game.constants import PlayOption


class Manager:
    def __init__(self, SCREENRECT):
        pygame.init()
        flags = pygame.NOFRAME | pygame.FULLSCREEN
        self.bestDepth = pygame.display.mode_ok(SCREENRECT.size, flags)
        self.surface = pygame.display.set_mode(SCREENRECT.size, flags, depth=self.bestDepth)
        self.surface.fill((255, 255, 255, 255))

        self.clock = pygame.time.Clock()

        # Modules states
        self.game_running = False
        self.menu_running = True

        # pygame.display.toggle_fullscreen()
        self.menu = menu.Menu(self)
        self.game = game.Game(self)

    def game_start(self, option: int):
        self.menu_running = False
        self.game.setMode(option)
        self.game_running = True

    def menu_start(self):
        self.game_running = False
        self.menu_running = True

    def run(self):
        self.menu_start()
        while True:
            if self.menu_running:
                self.menu.run()
            else:
                self.game.run()
