import os.path as op

from opster import command
from tornado import web, ioloop
from sockjs.tornado import SockJSRouter

from gomoku.api import ApiServer


ROOT = op.join(op.dirname(__file__), '..')


class IndexHandler(web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.finish(file(op.join(ROOT, 'static/index.html')).read())


@command()
def main(port=('p', 9999, 'port to listen on')):
    '''Start Gomoku server
    '''
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
    main.command()
