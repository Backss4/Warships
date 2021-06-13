import sys
import pygame
import pygame_gui
from game.constants import PlayOption
from game.utils import W, H
from game.game_internals import board


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
        # self.xd = pygame_gui.elements.UIImage(
        #     relative_rect=pygame.Rect((125, 100),
        #                               (W(700), H(364))),
        #     manager=self.uimanager,
        #     image_surface=self.pola)
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

    def handle_events(self):
        #print('Handle events')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.go_back_button:
                        self.manager.menu_start()
                    elif event.ui_element == self.send_button:
                        if self.input_line.get_text() != '':
                            self.messages.html_text = self.messages.html_text + self.input_line.get_text() + '<br>'
                            self.messages.rebuild()
                            self.input_line.set_text('')
            self.uimanager.process_events(event)

    def update(self, update_time):
        #print('Update')
        self.running = self.manager.game_running
        self.uimanager.update(update_time)

    def draw(self):
        #print('Draw')
        self.surface.blit(self.__background, (0, 0))
        pygame.draw.line(self.surface, (255, 255, 255), (0, 100), (self.surface.get_width(), 100))
        self.board.draw()
        self.enemy_board.draw()
        self.uimanager.draw_ui(self.surface)

    def set_mode(self, mode):
        pass

    def run(self):
        print('In game_internals')
        while self.running:
            time_delta = self.manager.clock.tick(60) / 1000.0
            self.handle_events()
            self.update(time_delta)
            self.draw()
            pygame.display.update()
