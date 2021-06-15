from game.constants import H_SCALE_FACTOR, W_SCALE_FACTOR


def H(x) -> int:
    return round(x * H_SCALE_FACTOR)


def W(x) -> int:
    return round(x * W_SCALE_FACTOR)


def count_char(string, char):
    ret = 0
    for i in string:
        if i == char:
            ret += 1
    return ret
