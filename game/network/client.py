import logging
import socket, threading, select, pygame, queue, pickle
import traceback

from game.constants import Orientation, FieldStatus, EventTypes


class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.running = False
        self.message_queues = queue.Queue()
        self.thread = None

    def clearMsgQueue(self):
        with self.message_queues.mutex:
            self.message_queues.queue.clear()

    def cleanup(self):
        self.sock = None
        self.thread = None
        self.clearMsgQueue()

    def connect(self, address, port):
        #self.sock.settimeout(3)
        self.sock.connect((address, 64000))
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.setblocking(0)

    def start(self, address, port):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connect(address, port)
            self.connected = True
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
            return True
        except Exception as expt:
            self.running = False
            self.connected = False
            print('[CLIENT ERR]' + str(expt))
            return False

    def handleMessage(self, msg):
        type, msg = msg.split(':', 1)
        if type == 'CHAT_MESSAGE':
            event_data = {'user_type': EventTypes.CHAT_MESSAGE,
                          'msg': msg}
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, event_data))
        print(type)

    def run(self):
        last_heartbeat = 0
        self.clearMsgQueue()
        try:
            print('[CLIENT MSG] Started')
            input = [self.sock]
            output = [self.sock]
            self.running = True
            while self.running:
                readable, writable, exceptional = select.select(
                    input, output, input, 1)

                for s in readable:
                    data = s.recv(1)
                    if data == b'':
                        pass
                    elif data:
                        msg = b''
                        while data != b'\r' and data != b'\n':
                            msg += data
                            data = s.recv(1)
                        self.handleMessage(msg.decode('utf-8'))
                    else:
                        input.remove(s)
                        output.remove(s)

                for s in writable:
                    try:
                        next_msg = self.message_queues.get_nowait()
                    except queue.Empty:
                        pass #nic nie rob jezeli kolejka jest pusta, mowi sie trudno
                    else:
                        s.send(next_msg.encode('utf-8'))

                for s in exceptional:
                    input.remove(s)
                    output.remove(s)
                    self.running = False

            self.sock.close()
            self.connected = False
        except Exception as expt:
            traceback.print_tb(expt.__traceback__)
            print('[CLIENT ERR] ' + str(expt))
        finally:
            self.running = False
            self.connected = False

    def stop(self):
        self.running = False
        self.thread.join()
        self.cleanup()
        print('Zabito klienta')

    def add_message_to_queue(self, msg):
        self.message_queues.put(msg)
