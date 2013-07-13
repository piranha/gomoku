from nose.tools import eq_

from gomoku import utils


def test_drop():
    d = {'a': 1, 'b': 2}
    eq_(utils.drop(d, 'a'), {'b': 2})
    eq_(d, {'a': 1, 'b': 2})

def test_new_field():
    eq_(utils.empty_field(3), '   \n   \n   ')

def test_char_position():
    eq_(utils.field_char_position({'size': 3}, 1, 0), 4)
