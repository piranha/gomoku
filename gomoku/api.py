import json
import uuid

from sockjs.tornado import SockJSConnection

from gomoku.utils import empty_field, get_field_char, set_field_char, check_win


def m(type, value=''):
    return {'type': type, 'value': value}


class ApiServer(SockJSConnection):
    # {conn: {name, mode}}
    players = dict()

    # [{id, player1, player2, field, done}]
    games = []

    def __init__(self, *args, **kwargs):
        super(ApiServer, self).__init__(*args, **kwargs)
        self.info = {'name': '', 'mode': '', 'total': 0, 'won': 0, 'lost': 0}

    # general api

    def broadcast(self, lst, msg):
        super(ApiServer, self).broadcast(lst, json.dumps(msg))

    def send(self, msg):
        super(ApiServer, self).send(json.dumps(msg))

    def to_participants(self, game, msg):
        self.broadcast(self.participants(game), msg)

    # helpers

    def my_name(self):
        return self.players[self]['name']

    def by_name(self, name):
        for p, i in self.players.iteritems():
            if i['name'] == name:
                return p

    def participants(self, game):
        return self.by_name(game['player1']), self.by_name(game['player2'])

    def game(self, id):
        for game in self.games:
            if game['id'] == id:
                return game

    def check_win(self, game):
        c = check_win(game)
        if not c:
            return
        game['done'] = c
        p1, p2 = self.participants(game)
        p1, p2 = self.players[p1], self.players[p2]
        p1['total'] += 1
        p2['total'] += 1
        if c == ' ':
            return
        winner, loser = (p1, p2) if c == 'x' else (p2, p1)
        winner['won'] += 1
        loser['lost'] += 1

    # notification methods

    def bc_players(self):
        self.broadcast(self.players, m('players', len(self.players)))

    def send_games(self):
        self.send(m('games', self.games))

    def bc_games(self):
        self.broadcast([p for p, i in self.players.items() if i['name']],
                       m('games', self.games))

    def send_info(self):
        self.send(m('info', self.info))

    # sockjs handlers

    def on_open(self, info):
        self.players[self] = self.info
        self.bc_players()

    def on_close(self):
        del self.players[self]
        self.bc_players()

    def on_message(self, msg):
        msg = json.loads(msg)
        type = msg.get('type')
        value = msg.get('value')

        fn = getattr(self, 'handle_%s' % type, None)
        if fn:
            fn(value)
        else:
            print 'No handler for %s' % type

    # message handlers

    def handle_name(self, value):
        if value == None:
            self.info['name'] = None
        elif any((i['name'] == value) for p, i in self.players.iteritems()):
            self.send(m('name:error', 'Name is taken'))
        else:
            self.info['name'] = value
            self.send(m('name:success'))
            self.send(m('games', self.games))
        self.send_info()

    def handle_new(self, value):
        size = int(value.get('size', 15))
        inarow = int(value.get('inarow', 5))
        game = {'id': uuid.uuid4().hex[:6],
                'player1': None,
                'player2': None,
                'size': size,
                'inarow': inarow,
                'field': empty_field(size),
                'eventurn': False,
                'done': None}
        name = self.players[self]['name']
        game['player2' if value.get('second') else 'player1'] = name
        self.games.insert(0, game)
        self.bc_games()

    def handle_join(self, id):
        game = self.game(id)
        if not game['player1']:
            game['player1'] = self.my_name()
        elif not game['player2']:
            game['player2'] = self.my_name()
        self.bc_games()
        # self.to_participants(game, m('game', game['id']))

    def handle_turn(self, (id, (x, y))):
        game = self.game(id)
        name = self.my_name()

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

        self.check_win(game)
        self.bc_games()

        if not self.check_win(game):
            return

        self.games.remove(game)
        self.bc_games()
        for p in self.participants(game):
            if p:
                p.send_info()
