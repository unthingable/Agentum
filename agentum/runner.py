'Simulation runner'

# Rudiments of the worker code

import imp
import sys
import os
import pkgutil
import logging
import optparse
from agentum.simulation import Simulation
from agentum.server import Server

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def arg_parser():
    usage = "usage: %prog [options] [file]"
    parser = optparse.OptionParser(usage)

    parser.add_option("-s", dest="steps", default=100,
                      help="The number of simulation steps"
    )

    parser.add_option("-gui", dest="steps", default=100,
                      help="The number of simulation steps"
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
        for k,v in config.__dict__.items():
            if not k.startswith('_'):
                parser.add_option('--%s' % k,
                                  dest = k,
                                  default = v)

def update_module_config(options, module):
    config = getattr(module, 'config', None)
    if config:
        for k,v in config.__dict__.items():
            if not k.startswith('_'):
                setattr(config, k, getattr(options, k))
        log.debug("New config: %s" % config.__dict__)

def run_main():
    parser = arg_parser()
    simmodule = sys.argv[-1]
    module = load_module(simmodule)

    load_module_config(parser, module)
    options, args = parser.parse_args()
    update_module_config(options, module)

    if options.steps:
        setup = getattr(module, 'setup', None)
        if not setup:
            raise Exception("No setup() found in module %s" % module.__name__)
        log.info("Loading simulation %s" % module.__name__)
        sim = Simulation()
        setup(sim)

        steps = options.steps
        log.info("Running simulation %s for %d steps..." % (module.__name__, steps))
        # Much optimization todo
        for step in range(steps):
            log.debug("Step: %d" % step)
            # Run agents
            for agent in sim.agents:
                agent.run(sim)
            # Run metaagents
            for cell in sim.space.cells():
                for metaagent in sim.metaagents:
                    metaagent.run(sim, cell)
            # This is a good place to emit state updates and such
    else:
        # Load ZMQ control center and start the wait loop^H^H^H
        # For now, load a Server with a single simulation

        # log.info("Simulation loaded, waiting for control (not yet implemented)")
        # import time
        # while True:
        #     time.sleep(1)

        server = Server()
        server.load_simulation(module)
        server.loop()

def load_module(simmodule):
    # options, args = parse_args()
    # simmodule = args[0]
    if os.path.isfile(simmodule):
        dirname, module_name = os.path.split(simmodule)
        module_name = module_name.replace('.py','')
        module = imp.load_source(module_name, simmodule)
    else:
        raise Exception("Not a file: %s" % simmodule)
    return module
