import sys
import pygame
import pygame_gui


class Game:
    def __init__(self, manager):
        self.manager = manager
        self.surface = self.manager.surface
        self.uimanager = pygame_gui.UIManager(self.surface.get_size())
        self.running = self.manager.game_running

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.make_game_button:
                        self.m.game_start()
            self.manager.process_events(event)

    def run(self):
        while self.running:
            time_delta = self.manager.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(time_delta)
            self.draw()
            pygame.display.update()