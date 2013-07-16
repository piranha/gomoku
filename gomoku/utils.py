import re


def empty_field(n):
    return '\n'.join([' ' * n] * n)


def field_char_position(game, x, y):
    # size + 1 because there is need to account for newlines
    return x * (game['size'] + 1) + y


def get_field_char(game, x, y):
    return game['field'][field_char_position(game, x, y)]


def set_field_char(game, x, y, char):
    pos = field_char_position(game, x, y)
    game['field'] = game['field'][:pos] + char + game['field'][pos+1:]
    return game


def pad(l, i):
    return ' ' * i + l

def lenghten(s, l):
    return s + ' ' * (l - len(s))

def transpose(f):
    lines = f.split('\n')
    maxlen = max(map(len, lines))
    lines = map(lambda x: lenghten(x, maxlen), lines)
    return '\n'.join(map(lambda x: ''.join(x), zip(*lines)))

def check_win(game):
    RE = re.compile('(x{%(inarow)s}|o{%(inarow)s})' % game)

    field = game['field']

    # horizontal
    m = RE.search(field)
    if m:
        return m.groups()[0][0]

    # vertical
    m = RE.search(transpose(field))
    if m:
        return m.groups()[0][0]

    # rtl
    newfield = '\n'.join([pad(line, i) for i, line in
                          enumerate(field.split('\n'))])
    m = RE.search(transpose(newfield))
    if m:
        return m.groups()[0][0]

    # ltr
    l = len(field)
    newfield = '\n'.join([pad(line, l - i - 1) for i, line in
                          enumerate(field.split('\n'))])
    m = RE.search(transpose(newfield))
    if m:
        return m.groups()[0][0]

    return None
