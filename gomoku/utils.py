def drop(d, *keys):
    n = dict(d)
    for k in keys:
        del n[k]
    return n


def empty_field(n):
    return '\n'.join([' ' * n] * n)


def field_char_position(field, x, y):
    # size + 1 because there is need to account for newlines
    return x * (field['size'] + 1) + y

def get_field_char(field, x, y):
    return field[field_char_position(field, x, y)]

def set_field_char(field, x, y, char):
    pos = field_char_position(field, x, y)
    return field[:pos] + char + field[pos+1:]
