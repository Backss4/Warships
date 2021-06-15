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
        self.logo = pygame.image.load('logo4.png')
        self.main_menu = MainMenu(self, self.__m)
        self.options_menu = OptionsMenu(self)

    def handle_events(self):
        if self.state == MenuState.MAIN:
            self.main_menu.handle_events()
        elif self.state == MenuState.OPTIONS:
            self.options_menu.handle_events()

    def draw(self):
        self.surface.blit(self.__m.background, (0, 0))
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
            text='Wróć do menu',
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


class AddressInputMenu:
    def __init__(self, manager, surface):
        self.running = False
        self.__m = manager
        self.__surface = surface
        self.__uimanager = pygame_gui.UIManager(self.__surface.get_size(), 'data/themes/gameui.json')
        self.input_line = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.__surface.get_width() / 2 - 200, 600),
                                      (400, 50)),
            manager=self.__uimanager,
            object_id='#input'
        )
        self.send_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.__surface.get_width() / 2 + 50, 655),
                                      (150, 42)),
            text='Dołącz',
            manager=self.__uimanager,
            object_id='#send'
        )
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.__surface.get_width() / 2 - 200, 655),
                                      (150, 42)),
            text='Anuluj',
            manager=self.__uimanager,
            object_id='#send'
        )

    def handle_events(self):
        address = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.back_button:
                        address = None
                        self.running = False
                        self.__m.menu_start()
                    elif event.ui_element == self.send_button:
                        address = self.input_line.get_text()
                        self.running = False
            self.__uimanager.process_events(event)
        return address

    def update(self, update_time):
        self.__uimanager.update(update_time)

    def draw(self):
        self.__surface.blit(self.__m.background, (0, 0))
        self.__uimanager.draw_ui(self.__surface)

    def run(self):
        self.running = True
        address = None
        while self.running:
            time_delta = self.__m.clock.tick(60) / 1000.0
            address = self.handle_events()
            self.update(time_delta)
            self.draw()
            pygame.display.update()
        return address

    @staticmethod
    def get_address(manager, surface):
        dialog = AddressInputMenu(manager, surface)
        return dialog.run()

class ErrorMenu:
    def __init__(self, manager, surface, error):
        self.running = False
        self.__m = manager
        self.__surface = surface
        self.__uimanager = pygame_gui.UIManager(self.__surface.get_size(), 'data/themes/gameui.json')
        font = pygame.font.SysFont(None, 48)
        self.text = font.render(error, True, (255, 255, 255))
        self.back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.__surface.get_width() / 2 - 100, 655),
                                      (200, 42)),
            text='Wróć do menu',
            manager=self.__uimanager,
            object_id='#send'
        )

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.back_button:
                        self.running = False
                        self.__m.menu_start()
            self.__uimanager.process_events(event)

    def update(self, update_time):
        self.__uimanager.update(update_time)

    def draw(self):
        self.__surface.blit(self.__m.background, (0, 0))
        self.__surface.blit(self.text, (self.__surface.get_width() / 2 - self.text.get_width() / 2, 600))
        self.__uimanager.draw_ui(self.__surface)

    def run(self):
        self.running = True
        while self.running:
            time_delta = self.__m.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(time_delta)
            self.draw()
            pygame.display.update()
        return True

    @staticmethod
    def show(manager, surface, error):
        dialog = ErrorMenu(manager, surface, error)
        return dialog.run()