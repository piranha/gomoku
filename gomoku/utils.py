def drop(d, *keys):
    n = dict(d)
    for k in keys:
        del n[k]
    return n


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
