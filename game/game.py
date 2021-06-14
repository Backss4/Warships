import sys
import pygame
import pygame_gui
from game.constants import PlayOption, EventTypes
from game.utils import W, H
from game.game_internals import board
from game.network import server, client
from game.menu import AddressInputMenu


class Game:
    def __init__(self, manager):
        self.manager = manager
        self.surface = self.manager.surface
        self.running = False
        self.uimanager = pygame_gui.UIManager(self.surface.get_size(), 'data/themes/gameui.json')
        self.go_back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.surface.get_width() // 2 - 125, self.surface.get_height() // 2 + 100),
                                      (250, 50)),
            text='Wróc do menu',
            manager=self.uimanager)
        self.messages = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((self.surface.get_width() - 626, 100),
                                      (502, 500)),
            html_text='',
            manager=self.uimanager,
            object_id='#text_box'
        )
        self.input_line = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((self.surface.get_width() - 625, 600),
                                      (400, 50)),
            manager=self.uimanager,
            object_id='#input'
        )
        self.send_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.surface.get_width() - 225, 600),
                                      (100, 42)),
            text='Wyślij',
            manager=self.uimanager,
            object_id='#send'
        )
        self.board = board.Board(125, 101, 40, 40, self.surface)
        self.enemy_board = board.Board(600, 101, 40, 40, self.surface)
        self.__background = pygame.transform.scale(pygame.image.load('new_bg_4.jpeg'), self.surface.get_size())
        self.mode = PlayOption.NONE
        self.server = server.Server()
        self.client = client.Client()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.USEREVENT:
                if event.user_type == EventTypes.CHAT_MESSAGE:
                    self.messages.html_text = self.messages.html_text + event.msg + '<br>'
                    self.messages.rebuild()
                elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.go_back_button:
                        self.manager.menu_start()
                    elif event.ui_element == self.send_button:
                        if self.input_line.get_text() == '/dc':
                            self.client.stop()
                        elif self.input_line.get_text() != '':
                            self.client.add_message_to_queue(self.input_line.get_text() + '\n')
                        self.input_line.set_text('')
            self.uimanager.process_events(event)

    def update(self, update_time):
        self.running = self.manager.game_running
        if not self.running:
            if self.client.running:
                self.client.stop()
            if self.server.running:
                self.server.stop()
        self.uimanager.update(update_time)

    def draw(self):
        self.surface.blit(self.__background, (0, 0))
        pygame.draw.line(self.surface, (255, 255, 255), (0, 100), (self.surface.get_width(), 100))
        self.board.draw()
        self.enemy_board.draw()
        self.uimanager.draw_ui(self.surface)

    def set_mode(self, mode):
        if mode == PlayOption.CREATE:
            if not self.server.start():
                pass #pokaz blad
            if not self.client.start('localhost', 64000):
                pass #poakz blad
        elif mode == PlayOption.JOIN:
            self.running = False
            self.surface.blit(self.__background, (0, 0))
            address = AddressInputMenu.get_address(self.manager, self.surface)
            if self.client.start():
                self.running = True
            else:
                pass #tutaj bedziemy pokazywac błąd

    def run(self):
        while self.running:
            time_delta = self.manager.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(time_delta)
            self.draw()
            pygame.display.update()
