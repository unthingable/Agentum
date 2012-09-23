'Simulation runner'

# Rudiments of the worker code

import gevent
from gevent import monkey
from gevent.server import StreamServer
import imp
import sys
import os
import pkgutil
import logging
import optparse
import signal

from agentum.simulation import Simulation
from agentum import worker as w
from agentum import protocol

monkey.patch_all()

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


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

    worker = w.WorkerSerial()
    if not options.gui:
        pass
    else:
        # Load ZMQ control center and start the wait loop^H^H^H
        # For now, load a Server with a single simulation

        # log.info("Simulation loaded, waiting for control (not yet implemented)")
        # import time
        # while True:
        #     time.sleep(1)

        # worker = Server()
        # worker.load_simulation(module)
        # worker.loop()

        def handle(socket, address):
            socket.send("Welcome to simulation server\n")
            worker = w.WorkerSerial()
            class queue(object):
                def put(self, obj):
                    socket.send("%s\n" % obj)
            protocol.queue = queue()

            module = load_module(simmodule)
            worker.load(module)
            fileobj = socket.makefile()

            for command in fileobj:
                args = command.strip().split()
                if args[0] == 'quit':
                    break
                elif args[0] == 'step':
                    worker.step()
            # fileobj.readline()
            # worker.run(steps=2)
            socket.close()

        server = StreamServer(('127.0.0.1', 5000), handle)
        log.info("Starting server %s" % str(server))
        server.serve_forever()

        return
    worker.load(module)
    worker.run()


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
