import sys
import pygame
import pygame_gui
from game.constants import PlayOption, EventTypes, FieldStatus
from game.utils import W, H
from game.game_internals import board
from game.network import server, client
from game.menu import AddressInputMenu, ErrorMenu


class Game:
    def __init__(self, manager):
        self.manager = manager
        self.surface = self.manager.surface
        self.running = False
        self.uimanager = pygame_gui.UIManager(self.surface.get_size(), 'data/themes/gameui.json')
        self.go_back_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((self.surface.get_width() - 375, 845),
                                      (250, 50)),
            text='Wróć do menu',
            object_id='#back',
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
        self.board = board.Board(125, 101, 40, 40, self.surface, 'Twoja plansza')
        self.enemy_board = board.Board(600, 101, 40, 40, self.surface, 'Plansza przeciwnika')
        self.mode = PlayOption.NONE
        self.server = server.Server()
        self.client = client.Client()
        self.status = 0
        self.font = pygame.font.SysFont(None, 32)
        self.waiting_message = self.font.render('Oczekiwanie na przeciwnika', True, (255, 255, 255))
        self.game_end_message = self.font.render('Koniec gry', True, (255, 255, 255))
        commands = [
            '/putship x y długość kierunek - ustawianie statku',
            'kierunek:',
            '0 - lewo',
            '1 - prawo',
            '2 - góra',
            '3 - dół',
            '/shot x y - strzał'
        ]
        self.commands = []
        for cmd in commands:
            self.commands.append(self.font.render(cmd, True, (255, 255, 255)))
        self.ship_status = []
        self.error = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.USEREVENT:
                if event.user_type == EventTypes.GAME_EVENT:
                    if event.event_type == EventTypes.SERVER_FULL:
                        self.error = event.msg
                    elif event.event_type == EventTypes.SERVER_MESSAGE:
                        self.messages.html_text = event.msg + '<br>' + self.messages.html_text
                        self.messages.rebuild()
                    elif event.event_type == EventTypes.CHAT_MESSAGE:
                        self.messages.html_text = 'Przeciwnik: ' + event.msg + '<br>' + self.messages.html_text
                        self.messages.rebuild()
                    elif event.event_type == EventTypes.PUT_SHIP:
                        self.board.set_field_status(event.x, event.y, FieldStatus.SHIP)
                    elif event.event_type == EventTypes.FIELD_HIT:
                        if event.board == 1:
                            self.board.set_field_status(event.x, event.y, FieldStatus.DESTROYED)
                        else:
                            self.enemy_board.set_field_status(event.x, event.y, FieldStatus.DESTROYED)
                    elif event.event_type == EventTypes.FIELD_MISSED:
                        if event.board == 1:
                            self.board.set_field_status(event.x, event.y, FieldStatus.MISSED)
                        else:
                            self.enemy_board.set_field_status(event.x, event.y, FieldStatus.MISSED)
                    elif event.event_type == EventTypes.SHIP_STATUS:
                        self.ship_status.clear()
                        if event.count == 2:
                            self.ship_status.append(event.p1)
                            self.ship_status.append(event.p2)
                        else:
                            self.ship_status.append(event.p1)
                        print(self.ship_status)
                    elif event.event_type == EventTypes.GAME_STATE:
                        self.status = int(event.msg)
                    elif event.event_type == EventTypes.SERVER_ERROR or event.event_type == EventTypes.CLIENT_ERROR:
                        self.error = event.err
                elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.go_back_button:
                        self.manager.menu_start()
                    elif event.ui_element == self.send_button:
                        if self.input_line.get_text() != '':
                            if self.input_line.get_text()[0] == '/':
                                command = value = None
                                if self.input_line.get_text().count(' ') > 1:
                                    command, value = self.input_line.get_text().split(' ', 1)
                                else:
                                    command = self.input_line.get_text()
                                if command == '/rematch':
                                    self.client.add_message_to_queue('REMATCH:' + str(1) + '\n')
                                elif command == '/putship':
                                    if value == None:
                                        value = ''
                                    self.client.add_message_to_queue('PUT_SHIP:' + value + '\n')
                                elif command == '/shot':
                                    if value == None:
                                        value = ''
                                    self.client.add_message_to_queue('SHOT:' + value + '\n')
                                if command == '/dc':
                                    self.client.stop()
                            else :
                                self.messages.html_text = 'Ty: ' + self.input_line.get_text() + '<br>' + self.messages.html_text
                                self.messages.rebuild()
                                self.client.add_message_to_queue('CHAT_MESSAGE:' + self.input_line.get_text() + '\n')
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
        self.surface.blit(self.manager.background, (0, 0))
        # pygame.draw.line(self.surface, (255, 255, 255), (0, 100), (self.surface.get_width(), 100))
        help_rect = pygame.Rect((self.surface.get_width() - 145 - self.commands[0].get_width(), 650),
                                     (self.commands[0].get_width() + 20, self.commands[0].get_height() * 7 + 15))
        help_surface = pygame.Surface(pygame.Rect(help_rect).size, pygame.SRCALPHA)
        pygame.draw.rect(help_surface, (128, 128, 128, 200), help_surface.get_rect())
        self.surface.blit(help_surface, (help_rect.x, help_rect.y))
        i = 0
        for comm in self.commands:
            self.surface.blit(comm, (self.surface.get_width() - 135 - self.commands[0].get_width(), 660 + self.commands[0].get_height() * i))
            i += 1
        self.board.draw()
        self.enemy_board.draw()
        if self.status == 0:
            self.surface.blit(self.waiting_message, (125, 650))
        elif self.status == 1:
            if len(self.ship_status) == 1:
                to_draw = self.font.render('Twoje statki do rozmieszczenia:', True, (255, 255, 255))
                self.surface.blit(to_draw, (125, 650))
                i = 0
                for x in self.ship_status[0]:
                    int_key = int(x)
                    if int_key == 4:
                        to_draw = self.font.render('Czteromasztowce: ' + str(self.ship_status[0][x]), True,
                                                   (255, 255, 255))
                        self.surface.blit(to_draw, (125, 740 + to_draw.get_height() * i))
                        i += 1
                    elif int_key == 3:
                        to_draw = self.font.render('Trójmasztowce: ' + str(self.ship_status[0][x]), True, (255, 255, 255))
                        self.surface.blit(to_draw, (125, 740 + to_draw.get_height() * i))
                        i += 1
                    elif int_key == 2:
                        to_draw = self.font.render('Dwumasztowce: ' + str(self.ship_status[0][x]), True, (255, 255, 255))
                        self.surface.blit(to_draw, (125, 740 + to_draw.get_height() * i))
                        i += 1
                    elif int_key == 1:
                        to_draw = self.font.render('Jednomasztowce: ' + str(self.ship_status[0][x]), True, (255, 255, 255))
                        self.surface.blit(to_draw, (125, 740 + to_draw.get_height() * i))
                        i += 1
        elif self.status == 2 and len(self.ship_status) == 2:
            to_draw = self.font.render('Twoje statki:', True, (255, 255, 255))
            self.surface.blit(to_draw, (125, 700))
            i = 0
            for x in self.ship_status[0]:
                int_key = int(x)
                if int_key == 4:
                    to_draw = self.font.render('Czteromasztowce: ' + str(self.ship_status[0][x]), True, (255, 255, 255))
                    self.surface.blit(to_draw, (125, 740 + to_draw.get_height() * i))
                    i += 1
                elif int_key == 3:
                    to_draw = self.font.render('Trójmasztowce: ' + str(self.ship_status[0][x]), True, (255, 255, 255))
                    self.surface.blit(to_draw, (125, 740 + to_draw.get_height() * i))
                    i += 1
                elif int_key == 2:
                    to_draw = self.font.render('Dwumasztowce: ' + str(self.ship_status[0][x]), True, (255, 255, 255))
                    self.surface.blit(to_draw, (125, 740 + to_draw.get_height() * i))
                    i += 1
                elif int_key == 1:
                    to_draw = self.font.render('Jednomasztowce: ' + str(self.ship_status[0][x]), True, (255, 255, 255))
                    self.surface.blit(to_draw, (125, 740 + to_draw.get_height() * i))
                    i += 1
            to_draw = self.font.render('Wrogie statki:', True, (255, 255, 255))
            self.surface.blit(to_draw, (600, 700))
            i = 0
            for x in self.ship_status[1]:
                int_key = int(x)
                if int_key == 4:
                    to_draw = self.font.render('Czteromasztowce: ' + str(self.ship_status[1][x]), True,
                                               (255, 255, 255))
                    self.surface.blit(to_draw, (600, 740 + to_draw.get_height() * i))
                    i += 1
                elif int_key == 3:
                    to_draw = self.font.render('Trójmasztowce: ' + str(self.ship_status[1][x]), True, (255, 255, 255))
                    self.surface.blit(to_draw, (600, 740 + to_draw.get_height() * i))
                    i += 1
                elif int_key == 2:
                    to_draw = self.font.render('Dwumasztowce: ' + str(self.ship_status[1][x]), True, (255, 255, 255))
                    self.surface.blit(to_draw, (600, 740 + to_draw.get_height() * i))
                    i += 1
                elif int_key == 1:
                    to_draw = self.font.render('Jednomasztowce: ' + str(self.ship_status[1][x]), True, (255, 255, 255))
                    self.surface.blit(to_draw, (600, 740 + to_draw.get_height() * i))
                    i += 1
        elif self.status == 3:
            self.surface.blit(self.game_end_message, (125, 650))

        self.uimanager.draw_ui(self.surface)

    def set_mode(self, mode):
        if mode == PlayOption.CREATE:
            if not self.server.start() or not self.server.start_event.wait(5):
                self.error = 'Serwer nie mógł zostać uruchomiony'
                return False
            if not self.client.start('26.57.228.154', 64000):
                self.error = 'Klient nie mógł sie połączyć'
                return False
        elif mode == PlayOption.JOIN:
            address = AddressInputMenu.get_address(self.manager, self.surface)
            if address is None:
                return False
            elif address == '':
                self.error = 'Adres IP nie może być pusty'
                return False
            xd = self.client.start(address, 64000)
            if not xd:
                self.error = 'Klient nie mógł się połączyć'
                return False
        return True

    def cleanup(self):
        self.messages.html_text = ''
        self.messages.rebuild()
        self.board.clear()
        self.enemy_board.clear()
        self.status = 0

    def run(self):
        self.cleanup()
        while self.running:
            if self.error is not None:
                self.running = False
                if self.client.running:
                    self.client.stop()
                if self.server.running:
                    self.server.stop()
                ErrorMenu.show(self.manager, self.surface, self.error)
                self.error = None
            else:
                time_delta = self.manager.clock.tick(60) / 1000.0
                self.handle_events()
                self.update(time_delta)
                self.draw()
                pygame.display.update()
