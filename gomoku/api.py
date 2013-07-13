import json
import uuid

from sockjs.tornado import SockJSConnection

from gomoku.utils import drop, empty_field, get_field_char, set_field_char


def m(type, value=''):
    return {'type': type, 'value': value}


class ApiServer(SockJSConnection):
    # {conn: {name, mode}}
    players = dict()

    # [{id, player1, player2, field, done}]
    games = []

    def __init__(self, *args, **kwargs):
        super(ApiServer, self).__init__(*args, **kwargs)
        self.info = {'name': '', 'mode': ''}

    # general api

    def broadcast(self, lst, msg):
        super(ApiServer, self).broadcast(lst, json.dumps(msg))

    def send(self, msg):
        super(ApiServer, self).send(json.dumps(msg))

    def to_participants(self, game, msg):
        players = [self.by_name(game['player1']), self.by_name(game['player2'])]
        self.broadcast(players, msg)

    # game api

    def name(self):
        return self.players[self]['name']

    def by_name(self, name):
        for p, i in self.players.iteritems():
            if i['name'] == name:
                return p

    def game(self, id):
        for game in self.games:
            if game['id'] == id:
                return game

    def open_games(self):
        return map(lambda g: drop(g, 'field'),
                   filter(lambda x: not x['done'], self.games))

    def bc_players(self):
        self.broadcast(self.players, m('players', len(self.players)))

    def send_games(self):
        self.send(m('games', self.open_games()))

    def bc_games(self):
        self.broadcast([p for p, i in self.players.items() if i['name']],
                       m('games', self.open_games()))

    # message handlers

    def on_open(self, info):
        self.players[self] = self.info
        self.bc_players()

    def on_close(self):
        del self.players[self]
        self.bc_players()

    def on_message(self, msg):
        print msg
        msg = json.loads(msg)
        type = msg.get('type')
        value = msg.get('value')

        fn = getattr(self, 'handle_%s' % type, None)
        if fn:
            fn(value)
        else:
            print 'No handler for %s' % type

    def handle_name(self, value):
        if any((i['name'] == value) for p, i in self.players.iteritems()):
            self.send(m('name:error', 'Name is taken'))
        else:
            self.info['name'] = value
            self.send(m('name:success'))
            self.send_games()

    def handle_new(self, value):
        self.games.insert(0, {'id': uuid.uuid4().hex[:6],
                              'player1': self.players[self]['name'],
                              'player2': None,
                              'size': 15,
                              'inarow': 5,
                              'field': empty_field(15),
                              'eventurn': False,
                              'done': None})
        self.bc_games()

    def handle_join(self, id):
        game = self.game(id)
        if game['player2'] == None:
            game['player2'] = self.name()
        self.send_games()
        self.to_participants(game, m('game', game))

    def handle_open(self, id):
        self.send(m('open', self.game(id)))

    def handle_turn(self, (id, (x, y))):
        game = self.game(id)
        name = self.name()

        if None in (game['player2'], game['player1']):
            return self.send(m('turn:error', 'Not enough players'))

        if not ((name == game['player1']) ^ game['eventurn']):
            return self.send(m('turn:error', 'Not your turn'))

        if get_field_char(game, x, y) != ' ':
            return self.send(m('turn:error', 'Field is already used'))

        char = 'x' if name == game['player1'] else 'o'
        set_field_char(game, x, y, char)
        game['eventurn'] = not game['eventurn']
        self.send(m('turn:success'))
        self.to_participants(game, m('game', game))
