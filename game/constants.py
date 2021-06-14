from main import SCREENRECT

W = SCREENRECT.width
H = SCREENRECT.height
W2 = W // 2
H2 = H // 2
W_SCALE_FACTOR = W / 1920
H_SCALE_FACTOR = H / 1080


class AnimationState:
    OPEN = 0
    WAIT = 1
    CLOSE = 2


class MenuState:
    MAIN = 0
    OPTIONS = 1


class PlayOption:
    CREATE = 0
    JOIN = 1
    NONE = 2

class Orientation:
    LEFT = 0
    RIGHT = 1
    UP = 2
    DOWN = 3

class FieldStatus:
    EMPTY = 0
    SHIP = 1
    DESTROYED = 2

class EventTypes:
    CHAT_MESSAGE = 0
