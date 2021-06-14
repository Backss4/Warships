import platform
import pygame
import pygame_gui
from game import menu, game
from game.constants import PlayOption, MenuState


class Manager:
    def __init__(self, SCREENRECT):
        pygame.init()
        flags = pygame.NOFRAME | pygame.FULLSCREEN
        #flags = pygame.NOFRAME
        self.bestDepth = pygame.display.mode_ok(SCREENRECT.size, flags)
        self.surface = pygame.display.set_mode(SCREENRECT.size, flags, depth=self.bestDepth)
        self.surface.fill((255, 255, 255, 255))

        self.clock = pygame.time.Clock()
        self.background = pygame.transform.scale(pygame.image.load('new_bg_4.jpeg'), self.surface.get_size())

        # Modules states
        self.game_running = False
        self.menu_running = True

        # pygame.display.toggle_fullscreen()
        self.menu = menu.Menu(self)
        self.game = game.Game(self)

    def game_start(self, option: int):
        self.menu_running = False
        self.game.set_mode(option)
        self.game.running = self.game_running = True

    def menu_start(self):
        self.game_running = False
        self.menu.state = MenuState.MAIN
        self.menu.running = self.menu_running = True

    def run(self):
        self.menu_start()
        while True:
            if self.menu_running:
                self.menu.run()
            else:
                self.game.run()
