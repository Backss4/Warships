import sys
import pygame
import pygame_gui
from game.constants import MenuState, PlayOption
from game.utils import W, H


class Menu:
    def __init__(self, game_manager):
        self.__m = game_manager
        self.surface = self.__m.surface
        self.running = True
        self.state = MenuState.MAIN
        self.__background = pygame.transform.scale(pygame.image.load('new_bg_4.jpeg'), self.surface.get_size())
        self.logo = pygame.image.load('logo4.png')
        self.main_menu = MainMenu(self, self.__m)
        self.options_menu = OptionsMenu(self)

    def handle_events(self):
        if self.state == MenuState.MAIN:
            self.main_menu.handle_events()
        elif self.state == MenuState.OPTIONS:
            self.options_menu.handle_events()

    def draw(self):
        self.surface.blit(self.__background, (0, 0))
        if self.state == MenuState.MAIN:
            self.main_menu.draw()
        elif self.state == MenuState.OPTIONS:
            self.options_menu.draw()

    def update(self, time_delta):
        self.running = self.__m.menu_running
        if self.state == MenuState.MAIN:
            self.main_menu.update(time_delta)
        elif self.state == MenuState.OPTIONS:
            self.options_menu.update(time_delta)

    def forceStop(self):
        self.running = False

    def run(self):
        while self.running:
            time_delta = self.__m.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(time_delta)
            self.draw()
            pygame.display.update()


class MainMenu:
    def __init__(self, menu, game_manager):
        self.__menu = menu
        self.__surface = self.__menu.surface
        self.__uimanager = pygame_gui.UIManager(self.__surface.get_size(), 'data/themes/menu.json')
        self.__m = game_manager
        self.surface = self.__menu.surface
        self.logo = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect((self.surface.get_width() // 2 - 320, self.surface.get_height() // 2 - 450),
                                      (W(700), H(364))),
            manager=self.__uimanager,
            image_surface=self.__menu.logo)
        self.make_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.surface.get_width() // 2 - 125, self.surface.get_height() // 2 - 50),
                                      (W(250), 50)),
            text='Utwórz nową grę',
            manager=self.__uimanager)
        self.join_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.surface.get_width() // 2 - 125, self.surface.get_height() // 2),
                                      (W(250), 50)),
            text='Dołącz do gry',
            manager=self.__uimanager)
        self.options_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.surface.get_width() // 2 - 125, self.surface.get_height() // 2 + 50),
                                      (W(250), 50)),
            text='Opcje',
            manager=self.__uimanager)
        self.quit_game_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.surface.get_width() // 2 - 125, self.surface.get_height() // 2 + 100),
                                      (W(250), 50)),
            text='Wyjdź z gry',
            manager=self.__uimanager)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.make_game_button:
                        self.__m.game_start(PlayOption.CREATE)
                    elif event.ui_element == self.join_game_button:
                        self.__m.game_start(PlayOption.JOIN)
                    elif event.ui_element == self.options_game_button:
                        self.__menu.state = MenuState.OPTIONS
                    else:
                        sys.exit()
            self.__uimanager.process_events(event)

    def update(self, update_time):
        self.__uimanager.update(update_time)

    def draw(self):
        self.__uimanager.draw_ui(self.surface)


class OptionsMenu:
    def __init__(self, menu):
        self.__menu = menu
        self.__surface = self.__menu.surface
        self.__uimanager = pygame_gui.UIManager(self.__surface.get_size(), 'data/themes/menu.json')
        self.menu = menu
        self.surface = self.menu.surface
        self.go_back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.surface.get_width() // 2 - 125, self.surface.get_height() // 2 + 100),
                                      (250, 50)),
            text='Wróc do menu',
            manager=self.__uimanager)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.go_back_button:
                        self.menu.state = MenuState.MAIN
                    else:
                        sys.exit()
            self.__uimanager.process_events(event)

    def update(self, update_time):
        self.__uimanager.update(update_time)

    def draw(self):
        self.__uimanager.draw_ui(self.surface)
