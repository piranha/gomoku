from nose.tools import eq_

from gomoku import utils


def test_new_field():
    eq_(utils.empty_field(3), '   \n   \n   ')


def test_char_position():
    eq_(utils.field_char_position({'size': 3}, 1, 0), 4)


def test_check_win():
    def check(f, size=3, inarow=3):
        return utils.check_win({'field': f, 'size': size, 'inarow': inarow})
    eq_(check('   \n   \n   '), None)
    eq_(check('xxx\n   \n   '), 'x')
    eq_(check('o  \no  \no  '), 'o')
    eq_(check('  x\n x \nx  '), 'x')
    eq_(check('o  \n o \n  o'), 'o')
    eq_(check('''\
  o            
               
               
               
       o    x  
     oxxo  x   
     x oxxxoo  
    oxxooxoxoo 
     x  x   o  
     x       x 
     o        o
     x         
    o          
               
               ''', size=15, inarow=5), 'x')
    eq_(check('xxo\noox\nxxo'), ' ')
