import logging
import socket, threading, select, queue
import sys
import traceback

from game.constants import Orientation, FieldStatus

starting_messages = [
    'Witaj w grze statki<br>'
    'To wiadomość początkowa'

]

class Server:
    def __init__(self):
        threading.Thread.__init__(self)
        self.running = False
        self.sock = None
        self.players = 0
        self.p1_fields = [[FieldStatus.EMPTY for i in range(10)] for i in range(10)]
        self.p2_fields = [[FieldStatus.EMPTY for i in range(10)] for i in range(10)]
        self.thread = None

    def cleanup(self):
        self.players = 0
        self.p1_fields = [[FieldStatus.EMPTY for i in range(10)] for i in range(10)]
        self.p2_fields = [[FieldStatus.EMPTY for i in range(10)] for i in range(10)]
        self.sock = None
        self.thread = None

    def checkIfCanPut(self, board, x, y, length, orientation):
        if self.checkIfShip(board, x, y):
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
                        if self.checkIfShip(board, i, y):
                            return False
                    if x - length >= 0 and self.checkIfShip(board, x - length, y):
                        return False
                else:
                    if self.checkIfShip(board, x - 1, y):
                        return False
                if (y != 0 and self.checkIfShip(board, x - 1, y - 1)) or (
                        y != 9 and self.checkIfShip(board, x - 1, y + 1)):
                    return False

            if x != 9:
                if orientation == Orientation.RIGHT:
                    for i in range(x, x + length, 1):
                        if self.checkIfShip(board, i, y):
                            return False
                    if x + length <= 9 and self.checkIfShip(board, x + length, y):
                        return False
                else:
                    if self.checkIfShip(board, x + 1, y):
                        return False
                if (y != 0 and self.checkIfShip(board, x + 1, y - 1)) or (
                        y != 9 and self.checkIfShip(board, x + 1, y + 1)):
                    return False

            if y != 0:
                if orientation == Orientation.UP:
                    for i in range(y, y - length, -1):
                        if self.checkIfShip(board, x, i):
                            return False
                    if y + length >= 0 and self.checkIfShip(board, x, y - length):
                        return False
                else:
                    if self.checkIfShip(board, x, y - 1):
                        return False

            if y != 9:
                if orientation == Orientation.UP:
                    for i in range(y, y + length, 1):
                        if self.checkIfShip(board, x, i):
                            return False
                    if y + length <= 9 and self.checkIfShip(board, x, y + length):
                        return False
                else:
                    if self.checkIfShip(board, x, y + 1):
                        return False
            return True

    def checkIfShip(self, board, x, y):
        if board[x][y] == FieldStatus.SHIP:
            return True
        return False

    def putShipOnTheBoard(self, board, x, y, length, orientation):
        if self.checkIfCanPut(board, x, y, length, orientation):
            if orientation == Orientation.LEFT:
                for i in range(x, x - length, -1):
                    board[i][y] = FieldStatus.SHIP
            elif orientation == Orientation.RIGHT:
                for i in range(x, x + length, 1):
                    board[i][y] = FieldStatus.SHIP
            elif orientation == Orientation.DOWN:
                for i in range(y, y + length, 1):
                    board[x][i] = FieldStatus.SHIP
            elif orientation == Orientation.UP:
                for i in range(y, y - length, -1):
                    board[x][i] = FieldStatus.SHIP

    def start(self):
        try:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
            return True
        except Exception as expt:
            self.running = False
            self.connected = False
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
            while self.running:
                readable, writable, exceptional = select.select(
                    inputs, outputs, inputs, 1)
                for s in readable:
                    if s is self.sock:
                        connection, client_address = s.accept()
                        if self.players < 2:
                            self.players += 1
                            connection.setblocking(0)
                            inputs.append(connection)
                            outputs.append(connection)
                            message_queues[connection] = queue.Queue()
                            message_queues[connection].put('CHAT_MESSAGE:Dzień dobry\n')
                        else:
                            connection.send(bytes('Gra jest pełna!\n'.encode('utf-8')))
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
                            message_queues[s].put('CHAT_MESSAGE:' + msg.decode('utf-8') + '\n')
                        else:
                            self.players -= 1
                            del message_queues[s]
                            inputs.remove(s)
                            outputs.remove(s)
                            s.close()

                for s in writable:
                    if s in outputs: # sprawdz czy nie zostal usuniety z listy (połączenie nie zostało zerwane)
                        try:
                            next_msg = message_queues[s].get_nowait()
                        except queue.Empty:
                            pass  # nic nie rob jezeli kolejka jest pusta, mowi sie trudno
                        else:
                            s.send(next_msg.encode('utf-8'))

                for s in exceptional:
                    del message_queues[s]
                    inputs.remove(s)
                    outputs.remove(s)
                    s.close()

                # print('r: ' + str(readable))
                # print('w: ' + str(writable))
                # print('e:' + str(exceptional))

            self.sock.close()
        except Exception as expt:
            if self.sock:
                self.sock.close()
            traceback.print_tb(expt.__traceback__)
            print('[SERVER ERR] ' + str(expt))
        finally:
            self.running = False

    def stop(self):
        self.running = False
        self.thread.join() # czekaj az wątek się zakończy
        self.cleanup() # zresetuj klase
        print('Zabito serwer')

