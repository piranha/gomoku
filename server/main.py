import os.path as op
import json
import uuid

from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection


ROOT = op.join(op.dirname(__file__), '..')


def m(type, value=''):
    return {'type': type, 'value': value}


class ApiServer(SockJSConnection):
    # {conn: {name, mode}}
    players = dict()

    # set({id, player1, player2, field, done})
    games = set()

    def __init__(self, *args, **kwargs):
        super(ApiServer, self).__init__(*args, **kwargs)
        self.info = {'name': '', 'mode': ''}

    # general api

    def broadcast(self, lst, msg):
        super(ApiServer, self).broadcast(lst, json.dumps(msg))

    def send(self, msg):
        super(ApiServer, self).send(json.dumps(msg))

    # game api

    def open_games(self):
        return filter(self.games, lambda x: not x['done'])

    def bc_players(self):
        self.broadcast(self.players, m('players', len(self.players)))

    def send_games(self):
        self.send(m('games', self.open_games()))

    def bc_games(self):
        self.broadcast(filter(self.players, lambda x: x['name']),
                       m('games', self.open_games()))

    # message handlers

    def on_open(self, info):
        self.players[self] = self.info
        self.bc_players()
        # self.send_games()

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
        if any(i['name'] for p, i in self.players.iteritems()):
            self.send(m('name:error', 'Name is taken'))
        else:
            self.info['name'] = value
            self.send(m('name:success'))

    def handle_new(self, value):
            self.games.add({'id': uuid.uuid4().hex[:6],
                            'player1': self,
                            'player2': None,
                            'done': False})
            self.bc_games()


class IndexHandler(web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.finish(file(op.join(ROOT, 'static/index.html')).read())


def main(port):
    ApiRouter = SockJSRouter(ApiServer, '/api')

    app = web.Application(ApiRouter.urls + [
            (r'/', IndexHandler),
            (r'/(.*)', web.StaticFileHandler,
             {'path': op.join(ROOT, 'static')})
            ], debug=True)

    app.listen(port)
    print 'listening %s...' % port
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main(9999)
