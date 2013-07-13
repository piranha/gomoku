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


class NoCacheStaticFileHandler(web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")


@command()
def main(port=('p', 9999, 'port to listen on'),
         address=('a', '127.0.0.1', 'address to listen on'),
         dev=('', False, 'run in development mode')):
    '''Start Gomoku server
    '''
    ApiRouter = SockJSRouter(ApiServer, '/api')

    StaticFileHandler = (NoCacheStaticFileHandler if dev
                         else web.StaticFileHandler)

    app = web.Application(ApiRouter.urls + [
            (r'/', IndexHandler),
            (r'/(.*)', StaticFileHandler,
             {'path': op.join(ROOT, 'static')})
            ], debug=dev)

    app.listen(port, address)
    print 'listening %s:%s...' % (address, port)
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main.command()
