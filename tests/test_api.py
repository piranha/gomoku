import json

from nose.tools import eq_

from gomoku.api import ApiServer


class TestApi(ApiServer):
    def __init__(self, *args, **kwargs):
        super(TestApi, self).__init__(*args, **kwargs)
        self.players = {}
        self.games = []
        self.sent = []
        self.bcasted = []
        self.players[self] = self.info

    def send(self, data):
        self.sent.append(data)

    def broadcast(self, dst, data):
        self.bcasted.append((dst, data))


def test_name():
    a = TestApi(None)
    a.handle_name('test')
    eq_(a.sent, [{'type': 'name:success', 'value': ''},
                 {'type': 'games', 'value': []},
                 {'type': 'info', 'value': {'won': 0, 'total': 0, 'name': 'test', 'lost': 0, 'mode': ''}}])
    eq_(a.bcasted, [])


def test_new():
    a = TestApi(None)
    a.handle_name('test')
    a.handle_new({'size': 3, 'inarow': 3})
    gid = a.games[0]['id']
    eq_(a.bcasted[0], ([a], {'type': 'games', 'value': [{'id': gid, 'player2': None, 'field': '   \n   \n   ', 'player1': 'test', 'inarow': 3, 'done': None, 'eventurn': False, 'size': 3}]}))


def test_join():
    a = TestApi(None)
    a.handle_name('test')
    a.handle_new({'size': 3, 'inarow': 3})
    gid = a.games[0]['id']

    b = TestApi(None)
    b.handle_name('qwe')

    # connect two instances
    a.players.update(b.players)
    b.players = a.players
    b.games = a.games

    b.handle_join(gid)

    eq_(set(b.bcasted[0][0]), set([a, b])) # somehow here order is sometimes different...
    eq_(b.bcasted[0][1], {'type': 'games', 'value': [{'id': gid, 'player2': 'qwe', 'field': '   \n   \n   ', 'player1': 'test', 'inarow': 3, 'done': None, 'eventurn': False, 'size': 3}]})


def test_turn():
    a = TestApi(None)
    a.handle_name('test')
    a.handle_new({'size': 3, 'inarow': 3})
    gid = a.games[0]['id']

    b = TestApi(None)
    b.handle_name('qwe')

    # connect two instances
    a.players.update(b.players)
    b.players = a.players
    b.games = a.games

    b.handle_join(gid)

    a.bcasted = []
    a.handle_turn((gid, (0, 0)))

    eq_(set(b.bcasted[0][0]), set([a, b])) # somehow here order is sometimes different...
    eq_(a.bcasted[0][1], {'type': 'games', 'value': [{'id': gid, 'player2': 'qwe', 'field': 'x  \n   \n   ', 'player1': 'test', 'inarow': 3, 'done': None, 'eventurn': True, 'size': 3}]})
