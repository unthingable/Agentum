'Simulation runner'

# Rudiments of the worker code

import logging
import argparse
import signal
import mimetypes
try:
    import ipdb as pdb
except:
    import pdb

from . import settings

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(settings.LOGLEVEL)


def dbhandler(signum, frame):
    pdb.set_trace()

signal.signal(signal.SIGQUIT, dbhandler)

# TODO: extract fields from sim and add to arguments


def arg_parser():
    parser = argparse.ArgumentParser()

    # parser.add_option("-s", dest="steps", default=100,
    #                   help="The number of simulation steps"
    #                   )

    parser.add_argument("-t", dest="telnet",
                      action="store_true",
                      help="Launch plain telnet console"
                      )
    parser.add_argument("-w", dest="web",
                      action="store_true",
                      help="Launch websocket server"
                      )
    parser.add_argument("-d", dest="debug",
                      action="store_true",
                      help="Turn on debugging output"
                      )

    parser.add_argument('module')

    return parser


# rudimentary, needs work
def load_module_config(parser, module):
    config = getattr(module, 'config', None)
    if config:
        for k, v in config.__dict__.items():
            if not k.startswith('_'):
                parser.add_option('--%s' % k,
                                  dest=k,
                                  default=v)


def update_module_config(options, module):
    config = getattr(module, 'config', None)
    if config:
        for k, v in config.__dict__.items():
            if not k.startswith('_'):
                setattr(config, k, getattr(options, k))
        log.debug("New config: %s" % config.__dict__)


def run_main():

    parser = arg_parser()
    args = parser.parse_args()
    simmodule = args.module
    # module = load_module(simmodule)

    # load_module_config(parser, module)

    #worker = w.WorkerSerial()
    # if not options.gui:
    #     worker.load(module)
    #     worker.run()

    if args.debug:
        log.setLevel(logging.DEBUG)
        settings.LOGLEVEL = logging.DEBUG
        log.debug('Enabled debugging')

    from agentum import worker as w
    from agentum import protocol
    from agentum.server import WorkerCmd
    from agentum.worker import load_sim

    if args.web:
        import gevent
        from gevent import monkey; monkey.patch_all()
        from gevent.server import StreamServer
        # gevent.signal(signal.SIGQUIT, dbhandler)
        # gevent.signal(signal.SIGTERM, gevent.shutdown)
        # gevent.signal(signal.SIGHUP, gevent.shutdown)

        import os.path
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler

        def handle(ws):
            log.debug("Connected")

            def push(obj):
                ws.send(obj)
            protocol.push = push

            worker = load_sim(simmodule)
            cmd = WorkerCmd(worker)

            while True:
                m = ws.receive()
                log.debug("Received: %s" % m)
                if cmd.onecmd(m):
                    break

        def app(environ, start_response):
            if environ['PATH_INFO'] == '/test':
                start_response("200 OK", [('Content-Type', 'text/plain')])
                return ["Yes this is a test!"]
            elif environ['PATH_INFO'] == "/data":
                handle(environ['wsgi.websocket'])
            else:
                path = environ['PATH_INFO'].strip('/') or 'grid.html'
                FILE = os.path.join(os.path.dirname(__file__),
                                    'static',
                                    path)
                #import ipdb; ipdb.set_trace()
                if os.path.isfile(FILE):
                    response_body = open(FILE).read()
                    status = '200 OK'
                    mimetype = mimetypes.guess_type(FILE)[0]
                    headers = [('Content-type', mimetype),
                               ('Content-Length', str(len(response_body)))]
                    start_response(status, headers)
                    return [response_body]
                else:
                    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
                    return ['Not Found']

        ws_server = pywsgi.WSGIServer(
            ('', 9990), app,
            handler_class=WebSocketHandler)
        # http server: serves up static files
        # http_server = gevent.pywsgi.WSGIServer(
        #     ('', 8000),
        #     paste.urlparser.StaticURLParser(os.path.dirname(__file__)))
        print "Connect to http://localhost:9990/"
        ws_server.serve_forever()

    elif args.telnet:
        import gevent
        from gevent import monkey; monkey.patch_all()
        from gevent.server import StreamServer
        gevent.signal(signal.SIGQUIT, dbhandler)
        gevent.signal(signal.SIGTERM, gevent.shutdown)
        gevent.signal(signal.SIGHUP, gevent.shutdown)

        def handle(socket, address):
            log.debug("Connected: %s" % str(address))
            socket.send("Welcome to simulation server\n")

            def push(obj):
                socket.send("%s\n" % obj)
            protocol.push = push

            worker = load_sim(simmodule)
            fileobj = socket.makefile()

            cmd = WorkerCmd(worker, stdin=fileobj, stdout=fileobj)
            cmd.use_rawinput = False
            cmd.cmdloop()
            fileobj.close()
            socket.close()

            log.debug("Disconnected: %s" % str(address))

        server = StreamServer(('127.0.0.1', 5000), handle)
        log.info("Starting server %s" % str(server))
        server.serve_forever()

        return
    else:
        # def push(obj):
        #     socket.send("%s\n" % obj)
        # protocol.push = push

        worker = load_sim(simmodule)

        cmd = WorkerCmd(worker)
        # cmd.use_rawinput = False
        cmd.cmdloop()
