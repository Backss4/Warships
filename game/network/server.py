import json
import queue
import random
import select
import socket
import threading
import time
import traceback
import pygame

from game.constants import Orientation, FieldStatus, EventTypes
from game.utils import count_char

starting_messages = [
    'Witaj w grze statki<br>'
    'To wiadomość początkowa'

]

MAP = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3,
    'e': 4,
    'f': 5,
    'g': 6,
    'h': 7,
    'i': 8,
    'j': 9
}


class Board:
    def __init__(self):
        self.board = [[FieldStatus.EMPTY for i in range(10)] for i in range(10)]

    def setStatus(self, x, y, status):
        self.board[x][y] = status

    def checkIfShip(self, x, y):
        if self.board[x][y] == FieldStatus.SHIP:
            return True
        return False

    def checkIfMissed(self, x, y):
        if self.board[x][y] == FieldStatus.MISSED:
            return True
        return False

    def checkIfDestroyed(self, x, y):
        if self.board[x][y] == FieldStatus.DESTROYED:
            return True
        return False

    def checkIfCanPut(self, x, y, length, orientation):
        if self.checkIfShip(x, y):
            return False
        elif x - length + 1 < 0 and orientation == Orientation.LEFT:
            return False
        elif x + length - 1 > 9 and orientation == Orientation.RIGHT:
            return False
        elif y - length + 1 < 0 and orientation == Orientation.UP:
            return False
        elif y + length - 1 > 9 and orientation == Orientation.DOWN:
            return False
        else:
            if x != 0:
                if orientation == Orientation.LEFT:
                    for i in range(x, x - length, -1):
                        if self.checkIfShip(i, y):
                            return False
                    if x - length >= 0 and self.checkIfShip(x - length, y):
                        return False
                else:
                    if self.checkIfShip(x - 1, y):
                        return False
                if (y != 0 and self.checkIfShip(x - 1, y - 1)) or (
                        y != 9 and self.checkIfShip(x - 1, y + 1)):
                    return False

            if x != 9:
                if orientation == Orientation.RIGHT:
                    for i in range(x, x + length, 1):
                        if self.checkIfShip(i, y):
                            return False
                    if x + length <= 9 and self.checkIfShip(x + length, y):
                        return False
                else:
                    if self.checkIfShip(x + 1, y):
                        return False
                if (y != 0 and self.checkIfShip(x + 1, y - 1)) or (
                        y != 9 and self.checkIfShip(x + 1, y + 1)):
                    return False

            if y != 0:
                if orientation == Orientation.UP:
                    for i in range(y, y - length, -1):
                        if self.checkIfShip(x, i):
                            return False
                    if y + length >= 0 and self.checkIfShip(x, y - length):
                        return False
                else:
                    if self.checkIfShip(x, y - 1):
                        return False

            if y != 9:
                if orientation == Orientation.UP:
                    for i in range(y, y + length, 1):
                        if self.checkIfShip(x, i):
                            return False
                    if y + length <= 9 and self.checkIfShip(x, y + length):
                        return False
                else:
                    if self.checkIfShip(x, y + 1):
                        return False
            return True


class Player:
    def __init__(self):
        self.board = Board()
        self.ships = {4: [], 3: [], 2: [], 1: []}
        self.ships_count = {4: 0, 3: 0, 2: 0, 1: 0}
        self.all_ships_count = 0

    def checkShipsCount(self, length):
        if self.ships_count[length] < 5 - length:
            return True
        return False

    def getAvailableShips(self):
        ships = {4: 1, 3: 2, 2: 3, 1: 4}
        for ship in ships:
            ships[ship] -= self.ships_count[ship]
        return ships

    def putShipOnTheBoard(self, x, y, length, orientation):
        ship = []
        if self.board.checkIfCanPut(x, y, length, orientation):
            if orientation == Orientation.LEFT:
                for i in range(x, x - length, -1):
                    ship.append((i, y))
                    self.board.setStatus(i, y, FieldStatus.SHIP)
            elif orientation == Orientation.RIGHT:
                for i in range(x, x + length, 1):
                    ship.append((i, y))
                    self.board.setStatus(i, y, FieldStatus.SHIP)
            elif orientation == Orientation.DOWN:
                for i in range(y, y + length, 1):
                    ship.append((x, i))
                    self.board.setStatus(x, i, FieldStatus.SHIP)
            elif orientation == Orientation.UP:
                for i in range(y, y - length, -1):
                    ship.append((x, i))
                    self.board.setStatus(x, i, FieldStatus.SHIP)
            self.all_ships_count += 1
            self.ships_count[length] += 1
            self.ships[length].append(ship)
            print(self.ships)
        return ship

    def shoot(self, x, y):
        check = False
        if self.board.checkIfMissed(x, y) or self.board.checkIfDestroyed(x, y):
            return -1
        elif self.board.checkIfShip(x, y):
            self.board.setStatus(x, y, FieldStatus.DESTROYED)
            for key in self.ships:  # sprawdz statki
                if self.ships[key]:  # jezeli sa jakies statki o danej dlugosci
                    for ship in self.ships[key]:  # sprawdz kazdy statek po kolei
                        for field in ship:  # sprawdz kazde pole po kolei
                            if field == (x, y):  # jezeli pole nalezy do statku to je usun
                                ship.remove(field)
                                check = True
                                break  # mozna wyjsc bo nic nie mamy juz do roboty
                        if check:  # tutaj wiemy ze znalezlismy pole i musimy sprawdzic czy nie zniszczylismy obecnego statku
                            if not ship:
                                self.ships[key].remove(ship)
                                self.ships_count[key] -= 1
                                self.all_ships_count -= 1
                            break
                if check:  # wczesniej usunelismy statek
                    break
            return EventTypes.FIELD_HIT
        else:
            return EventTypes.FIELD_MISSED


class Server:
    def __init__(self):
        self.start_event = threading.Event()
        self.running = False
        self.sock = None
        self.players = {}
        self.thread = None

    def cleanup(self):
        self.players = {}
        self.sock = None
        self.thread = None
        self.start_event.clear()

    def start(self):
        try:
            self.cleanup()
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
            return True
        except Exception as expt:
            self.running = False
            print('[SERVER ERR] ' + str(expt))
            return False

    def run(self):
        try:
            print('[SERVER MSG] Serwer startuje')
            self.running = True
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.sock.bind(('26.57.228.154', 64000))
            self.sock.setblocking(0)
            self.sock.listen(0)
            inputs = [self.sock]
            outputs = []
            message_queues = {}
            kolejka = None
            p1 = p2 = None
            players = {}
            heartbeat = {}
            game_state = 0
            self.start_event.set()
            while self.running:
                readable, writable, exceptional = select.select(
                    inputs, outputs, inputs, 1)

                if game_state == 1 and p1 is not None and p2 is not None:
                    if players[p1].all_ships_count == 10 and players[p2].all_ships_count == 10:
                        message_queues[p1].put(
                            'SHIP_STATUS:' + json.dumps(players[p1].ships_count) + '#' +
                            json.dumps(players[p2].ships_count) + '\n')
                        message_queues[p2].put(
                            'SHIP_STATUS:' + json.dumps(players[p2].ships_count) + '#' +
                            json.dumps(players[p2].ships_count) + '\n')
                        for c in outputs:
                            message_queues[c].put('GAME_STATE:' + str(2) + '\n')
                        kolejka = random.choice([p1, p2])
                        if kolejka == p1:
                            message_queues[p2].put(
                                'SERVER_MESSAGE:[INFORMACJA] Twój przeciwnik zaczyna!\n')
                        else:
                            message_queues[p1].put(
                                'SERVER_MESSAGE:[INFORMACJA] Twój przeciwnik zaczyna!!\n')
                        message_queues[kolejka].put(
                            'SERVER_MESSAGE:[INFORMACJA] Zaczynasz!\n')
                        game_state = 2

                for s in readable:
                    if s is self.sock:
                        connection, client_address = s.accept()
                        if len(players) < 2:
                            connection.setblocking(0)
                            inputs.append(connection)
                            outputs.append(connection)
                            message_queues[connection] = queue.Queue()
                            message_queues[connection].put('SERVER_MESSAGE:Połączyłeś się z grą!\n')
                            heartbeat[connection] = 0
                            if not players:
                                p1 = connection
                                players[p1] = Player()
                                message_queues[p1].put('SHIP_STATUS:' + json.dumps(players[p1].getAvailableShips()) + '\n')
                                game_state = 0
                            else:
                                p2 = connection
                                players[p2] = Player()
                                message_queues[p2].put('SHIP_STATUS:' + json.dumps(players[p2].getAvailableShips()) + '\n')
                                for c in outputs:
                                    message_queues[c].put('GAME_STATE:' + str(1) + '\n')
                                game_state = 1
                        else:
                            connection.send(bytes('SERVER_FULL:Gra jest pełna!\n'.encode('utf-8')))
                            connection.close()
                    else:
                        data = s.recv(1)
                        if data == b'':
                            pass
                        elif data:
                            msg = b''
                            while data != b'\r' and data != b'\n':
                                msg += data
                                data = s.recv(1)
                            msg = msg.decode('utf-8')
                            if msg == 'heartbeat':
                                pass
                            else:
                                try:
                                    type, msg = msg.split(':', 1)
                                except ValueError:
                                    message_queues[s].put(
                                        'SERVER_MESSAGE:[BŁĄD] Błędne dane przekazane do serwera!\n')
                                else:
                                    if type == 'CHAT_MESSAGE':
                                        for soc in outputs:
                                            if soc is not s:
                                                message_queues[soc].put(type + ':' + msg + '\n')
                                    elif type == 'SHOT':
                                        if count_char(msg, ' ') == 1:
                                            try:
                                                x, y = msg.split(' ', 1)
                                                x = x.lower()
                                                y = int(y) - 1
                                                if game_state == 1 or game_state == 0:
                                                     message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nie możesz strzelać przed rozpoczęciem gry!\n')
                                                elif game_state == 3:
                                                     message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nie możesz strzelać po skończonej grze!\n')
                                                elif not (x in MAP):
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nieprawidlowa współrzędna X!\n')
                                                elif not (0 <= y <= 9):
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nieprawidlowa współrzędna Y!\n')
                                                elif kolejka != s:
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Poczekaj na swoją kolej!\n')
                                                else:
                                                    x = MAP[x]
                                                    if s == p1:
                                                        r = players[p2].shoot(x, y)
                                                        if r == EventTypes.FIELD_HIT:
                                                            message_queues[p2].put(
                                                                'FIELD_HIT:' + str(x) + '#' + str(y) + '#' + str(1) + '\n')
                                                            message_queues[s].put(
                                                                'FIELD_HIT:' + str(x) + '#' + str(y) + '#' + str(2) + '\n')
                                                            message_queues[p2].put(
                                                                'SHIP_STATUS:' + json.dumps(players[p2].ships_count) + '#' +
                                                                json.dumps(players[p1].ships_count) + '\n')
                                                            message_queues[s].put(
                                                                'SHIP_STATUS:' + json.dumps(players[p1].ships_count) + '#' +
                                                                json.dumps(players[p2].ships_count) + '\n')
                                                            message_queues[s].put(
                                                                'SERVER_MESSAGE:[INFORMACJA] Trafiony!\n')
                                                            message_queues[p2].put(
                                                                'SERVER_MESSAGE:[INFORMACJA] Przeciwnik trafił w twój statek!\n')
                                                            if players[p2].all_ships_count == 0:
                                                                for ll in outputs:
                                                                    message_queues[ll].put('GAME_STATE:' + str(3) + '\n')
                                                                message_queues[p1].put(
                                                                    'SERVER_MESSAGE:[INFORMACJA] Wygrałeś!\n')
                                                                message_queues[p2].put(
                                                                    'SERVER_MESSAGE:[INFORMACJA] Przegrałeś.\n')
                                                                game_state = 3
                                                        elif r == EventTypes.FIELD_MISSED:
                                                            message_queues[p2].put(
                                                                'FIELD_MISSED:' + str(x) + '#' + str(y) + '#' + str(
                                                                    1) + '\n')
                                                            message_queues[s].put(
                                                                'FIELD_MISSED:' + str(x) + '#' + str(y) + '#' + str(
                                                                    2) + '\n')
                                                            message_queues[s].put(
                                                                'SERVER_MESSAGE:[INFORMACJA] Pudło, teraz kolej twojego przeciwnika!\n')
                                                            message_queues[p2].put(
                                                                'SERVER_MESSAGE:[INFORMACJA] Przeciwnik spudłował, teraz twoja kolej!\n')
                                                            kolejka = p2
                                                        elif r == -1:
                                                            message_queues[s].put(
                                                                'SERVER_MESSAGE:[BŁĄD] Nie możesz strzelić w to miejsce!\n')
                                                    else:
                                                        r = players[p1].shoot(x, y)
                                                        if r == EventTypes.FIELD_HIT:
                                                            message_queues[p1].put(
                                                                'FIELD_HIT:' + str(x) + '#' + str(y) + '#' + str(1) + '\n')
                                                            message_queues[s].put(
                                                                'FIELD_HIT:' + str(x) + '#' + str(y) + '#' + str(2) + '\n')
                                                            message_queues[p1].put(
                                                                'SHIP_STATUS:' + json.dumps(players[p1].ships_count) + '#' +
                                                                json.dumps(players[p2].ships_count) + '\n')
                                                            message_queues[s].put(
                                                                'SHIP_STATUS:' + json.dumps(players[p2].ships_count) + '#' +
                                                                json.dumps(players[p1].ships_count) + '\n')
                                                            message_queues[s].put(
                                                                'SERVER_MESSAGE:[INFORMACJA] Trafiony!\n')
                                                            message_queues[p1].put(
                                                                'SERVER_MESSAGE:[INFORMACJA] Przeciwnik trafił w twój statek!\n')
                                                            if players[p1].all_ships_count == 0:
                                                                for ll in outputs:
                                                                    message_queues[ll].put('GAME_STATE:' + str(3) + '\n')
                                                                message_queues[s].put(
                                                                    'SERVER_MESSAGE:[INFORMACJA] Wygrałeś!\n')
                                                                message_queues[p1].put(
                                                                    'SERVER_MESSAGE:[INFORMACJA] Przegrałeś.\n')
                                                                game_state = 3
                                                        elif r == EventTypes.FIELD_MISSED:
                                                            message_queues[p1].put(
                                                                'FIELD_MISSED:' + str(x) + '#' + str(y) + '#' + str(
                                                                    1) + '\n')
                                                            message_queues[s].put(
                                                                'FIELD_MISSED:' + str(x) + '#' + str(y) + '#' + str(
                                                                    2) + '\n')
                                                            message_queues[s].put(
                                                                'SERVER_MESSAGE:[INFORMACJA] Pudło, teraz kolej twojego przeciwnika!\n')
                                                            message_queues[p1].put(
                                                                'SERVER_MESSAGE:[INFORMACJA] Przeciwnik spudłował, teraz twoja kolej!\n')
                                                            kolejka = p1
                                                        elif r == -1:
                                                            message_queues[s].put(
                                                                'SERVER_MESSAGE:[BŁĄD] Nie możesz strzelić w to miejsce!\n')
                                            except ValueError:
                                                message_queues[s].put(
                                                    'SERVER_MESSAGE:[BŁĄD] Podano błędne parametry komendy!\n')
                                        else:
                                            message_queues[s].put(
                                                'SERVER_MESSAGE:Podana komenda posiada nieprawidłową ilość parametrów!\n')
                                    elif type == 'PUT_SHIP':
                                        if count_char(msg, ' ') == 3:
                                            try:
                                                x, y, length, direction = msg.split(' ', 3)

                                                x = x.lower()
                                                y = int(y) - 1
                                                length = int(length)
                                                direction = int(direction)

                                                if game_state == 0:
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Poczekaj na swojego przeciwnika!\n')
                                                elif game_state == 2:
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nie możesz układać statków podczas gry!\n')
                                                elif game_state == 3:
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nie możesz układać statków po skończonej grze!\n')
                                                elif not (x in MAP):
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nieprawidlowa współrzędna X!\n')
                                                elif not (0 <= y <= 9):
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nieprawidlowa współrzędna Y!\n')
                                                elif not (0 < length < 5):
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nieprawidlowa długość statku!\n')
                                                elif not (0 <= direction <= 3):
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nieprawidlowy kierunek!\n')
                                                elif players[s].all_ships_count == 10:
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Nie możesz rozstawić więcej statków!\n')
                                                elif not players[s].checkShipsCount(int(length)):
                                                    message_queues[s].put(
                                                        'SERVER_MESSAGE:[BŁĄD] Wykorzystałeś już wszystkie statki danego typu!\n')
                                                else:
                                                    x = MAP[x]
                                                    ship = players[s].putShipOnTheBoard(x, y, length, direction)
                                                    if ship:
                                                        for field in ship:
                                                            message_queues[s].put(
                                                                'PUT_SHIP:' + str(field[0]) + '#' + str(field[1]) + '\n')
                                                        message_queues[s].put(
                                                            'SHIP_STATUS:' + json.dumps(players[s].getAvailableShips()) + '\n')
                                                        message_queues[s].put(
                                                            'SERVER_MESSAGE:[INFORMACJA] Postawiłeś statek!\n')
                                                        if players[s].all_ships_count == 10:
                                                            message_queues[s].put(
                                                                'SERVER_MESSAGE:[INFORMACJA] Rozstawiłeś wszystkie statki, poczekaj na przeciwnika.\n')
                                                    else:
                                                        message_queues[s].put(
                                                            'SERVER_MESSAGE:[BŁĄD] Nie możesz postawić statku w tym miejscu!\n')
                                            except ValueError:
                                                message_queues[s].put(
                                                    'SERVER_MESSAGE:[BŁĄD] Podano błędne parametry komendy!\n')
                                        else:
                                            message_queues[s].put(
                                                'SERVER_MESSAGE:Podana komenda posiada nieprawidłową ilość parametrów!\n')
                        else:
                            del message_queues[s]
                            del players[s]
                            inputs.remove(s)
                            outputs.remove(s)
                            if p1 == s:
                                p1 = None
                            elif p2 == s:
                                p2 = None
                            s.close()
                            event_data = {
                                'user_type': 'game_event',
                                'event_type': EventTypes.SERVER_ERROR,
                                'err': 'Drugi klient rozłączył się.'
                            }
                            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))

                for s in writable:
                    if s in outputs:  # sprawdz czy nie zostal usuniety z listy (połączenie nie zostało zerwane)
                        try:
                            next_msg = message_queues[s].get_nowait()
                        except queue.Empty:
                            if heartbeat[s] + 5 <= time.time():
                                s.send(bytes('heartbeat\n'.encode('utf-8')))
                                heartbeat[s] = time.time()
                        else:
                            s.send(next_msg.encode('utf-8'))

                for s in exceptional:
                    del message_queues[s]
                    del players[s]
                    inputs.remove(s)
                    outputs.remove(s)
                    if p1 == s:
                        p1 = None
                    elif p2 == s:
                        p2 = None
                    s.close()
                    event_data = {
                        'user_type': 'game_event',
                        'event_type': EventTypes.SERVER_ERROR,
                        'err': 'Drugi klient rozłączył się.'
                    }
                    pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
                    # powiedz grze że powinniśmy wyjść - rozłączenie jakiegoś gracza

                # if readable:
                #     print('r: ' + str(readable))
                # if writable:
                #     print('w: ' + str(writable))
                if exceptional:
                    print('e:' + str(exceptional))

            self.sock.close()
        except Exception as expt:
            if self.sock:
                self.sock.close()
            event_data = {
                'user_type': 'game_event',
                'event_type': EventTypes.SERVER_ERROR,
                'err': 'Drugi klient rozłączył się.'
            }
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
            print('[SERVER ERR] ' + str(expt))
        finally:
            self.running = False

    def stop(self):
        self.running = False
        self.thread.join()  # czekaj az wątek się zakończy
        self.cleanup()  # zresetuj klase
        print('Zabito serwer')
