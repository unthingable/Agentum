'Simulation runner'

# Rudiments of the worker code

import gevent
from gevent import monkey; monkey.patch_all()
from gevent.server import StreamServer
import imp
import sys
import os
import pkgutil
import logging
import optparse
import signal
import mimetypes

from agentum.simulation import Simulation
from agentum import worker as w
from agentum import protocol
from agentum.server import WorkerCmd

from . import settings

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(settings.LOGLEVEL)


def arg_parser():
    usage = "usage: %prog [options] [file]"
    parser = optparse.OptionParser(usage)

    parser.add_option("-s", dest="steps", default=100,
                      help="The number of simulation steps"
                      )

    parser.add_option("-g", dest="gui", default=False,
                      help="Launch the GUI"
                      )

    # How to add no argument options?
    # parser.add_option("-c", "--controller-wait", dest="wait", default=False,
    #                   help="Wait for controller connection")

    return parser
    options, args = parser.parse_args()
    # import ipdb; ipdb.set_trace()
    return options, args


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
    gevent.signal(signal.SIGQUIT, gevent.shutdown)
    gevent.signal(signal.SIGTERM, gevent.shutdown)
    gevent.signal(signal.SIGHUP, gevent.shutdown)

    parser = arg_parser()
    simmodule = sys.argv[-1]
    module = load_module(simmodule)

    load_module_config(parser, module)
    options, args = parser.parse_args()
    update_module_config(options, module)

    #worker = w.WorkerSerial()
    # if not options.gui:
    #     worker.load(module)
    #     worker.run()
    if options.gui:
        def handle(socket, address):
            log.debug("Connected: %s" % str(address))
            socket.send("Welcome to simulation server\n")
            worker = w.WorkerSerial()
            class queue(object):
                def put(self, obj):
                    socket.send("%s\n" % obj)
            protocol.queue = queue()

            module = load_module(simmodule)
            worker.load(module)
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
        import os.path
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
        from geventwebsocket import websocket


        def handle(ws):
            log.debug("Connected")
            worker = w.WorkerSerial()
            class queue(object):
                def put(self, obj):
                    ws.send(obj)
            protocol.queue = queue()

            module = load_module(simmodule)
            worker.load(module)
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
                    return None

        ws_server = pywsgi.WSGIServer(
            ('', 9990), app,
            handler_class=WebSocketHandler)
        # http server: serves up static files
        # http_server = gevent.pywsgi.WSGIServer(
        #     ('', 8000),
        #     paste.urlparser.StaticURLParser(os.path.dirname(__file__)))
        print "Connect to http://localhost:9990/"
        ws_server.serve_forever()

def load_module(simmodule):
    # options, args = parse_args()
    # simmodule = args[0]
    if os.path.isfile(simmodule):
        dirname, module_name = os.path.split(simmodule)
        module_name = module_name.replace('.py', '')
        module = imp.load_source(module_name, simmodule)
    else:
        raise Exception("Not a file: %s" % simmodule)
    return module
