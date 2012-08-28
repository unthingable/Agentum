'Simulation runner'

import imp
import sys
import os
import pkgutil
import logging
import optparse
from agentum.simulation import Simulation

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

def parse_args():
    usage = "usage: %prog [options] [file]"
    parser = optparse.OptionParser(usage)

    parser.add_option("-s", "--steps", dest="steps", default=100,
        help="The number of simulation steps"
    )
    parser.add_option("--no-wait", dest="nowait", default=False,
        help="Run the simulation instead of waiting for remote control"
    )

    options, args = parser.parse_args()

    return options, args

def run_main():
    options, args = parse_args()
    simmodule = args[0]
    module = load_module(simmodule
                         )
    setup = getattr(module, 'setup', None)
    if not setup:
        raise Exception("No setup() found in module %s" % module.__name__)
    log.info("Loading simulation %s" % module.__name__)
    sim = Simulation()
    setup(sim)

    if options.nowait:
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
        # Load ZMQ control center and start the wait loop
        log.info("Simulation loaded, waiting for control (not yet implemented)")
        import time
        while True:
            time.sleep(1)

def load_module(simmodule):
    options, args = parse_args()
    simmodule = args[0]
    if os.path.isfile(simmodule):
        dirname, module_name = os.path.split(simmodule)
        module_name = module_name.replace('.py','')
        module = imp.load_source(module_name, simmodule)
    else:
        raise Exception("Not a file: %s" % simmodule)
    return module