from nose.tools import eq_

from gomoku import utils


def test_new_field():
    eq_(utils.empty_field(3), '   \n   \n   ')


def test_char_position():
    eq_(utils.field_char_position({'size': 3}, 1, 0), 4)


def test_check_win():
    def check(f):
        return utils.check_win({'field': f, 'size': 3, 'inarow': 3})
    eq_(check('   \n   \n   '), None)
    eq_(check('xxx\n   \n   '), 'x')
    eq_(check('o  \no  \no  '), 'o')
    eq_(check('  x\n x \nx  '), 'x')
    eq_(check('o  \n o \n  o'), 'o')
