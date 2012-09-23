"""
Simulation server.

At this point the server is its own worker.
Once we come to the distributed phase we'll
separate the workers from the server.
"""

"""
LIST
LOAD (and reload if already loaded)
GET <sim id>    - return params
SET <sim id>
START <sim id>
STOP <sim id>
"""

"""
NOTE: gevent is slower (a lot!) when running on a VM:
http://stackoverflow.com/questions/10656953/redis-gevent-poor-performance-what-am-i-doing-wrong
"""

import logging
from cmd import Cmd
import gevent
from gevent.event import AsyncResult
from gevent.server import StreamServer
from gevent.pool import Group
from gevent.queue import Queue, Empty

from agentum.simulation import Simulation

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

step_event = AsyncResult()
result_queue = Queue()

def zrange(x):
    '''
    Like xrange, but go on forever if x is 0 (or None)
    '''
    x = x or -1
    y = 0
    while x != y:
        yield y
        y += 1


class Server(object):

    # clients = []
    # simulations = []
    # running_simulations = []

    # For now, a single simulation, no clients
    sim = None
    module = None

    _num_cells = 0

    def load(self, module):
        self.module = module
        setup = getattr(module, 'setup', None)
        if not setup:
            raise Exception("No setup() found in module %s" % module.__name__)
        log.info("Loading simulation %s" % module.__name__)

        #self.sim = Simulation()
        self.sim = module.simulation()
        setup(self.sim)

        # simulations.append(sim)
        # ...

    def run(self, steps=100):
        """
        Run the simulation for N steps. Set to 0 to run endlessly.
        """
        agent_group = Group()
        magent_group = Group()
        log.info("Running simulation %s for %d steps..." %
                 (self.module.__name__, steps))

        # Gentlemen, start your agents
        for agent in self.sim.agents:
            agent_group.add(gevent.spawn(self.step_agent, agent))
        for cell in self.sim.space.cells():
            magent_group.add(gevent.spawn(self.step_metaagent, cell))

        # TODO: remove
        self._num_cells = len(self.sim.space.cells())

        for n in zrange(steps):
            # TODO: get messages and stop if requested, otherwise:
            self.step(n)
        # Finally:
        step_event.set(-1)

        # Check agents for errors?
        agent_group.join()
        magent_group.join()

    def step(self, stepnum=-1):
        log.debug("Step: %d" % stepnum)

        if not step_event.ready():
            step_event.set(stepnum)

        # Wait for agents to do their thing
        finished = {'agent': set(), 'metaagent': set()}
        while True:
            if (len(finished['agent']) == len(self.sim.agents) and
                len(finished['metaagent']) == self._num_cells):
                break
            (stream, item) = result_queue.get()
            finished[stream].add(item)

        # sim = self.sim

        # # Much optimization todo

        # # Run agents
        # self.group.imap(self.step_agent, sim.agents)
        # # Run metaagents
        # self.group.imap(self.step_metaagent, sim.space.cells())
        # # This is a good place to emit state updates and such

    def stop(self):
        pass

    def step_agent(self, agent):
        while True:
            stepnum = step_event.get()
            if stepnum == -1:
                # We're done
                return
            agent.run(self.sim)
            # Report we're done with the step
            result_queue.put(('agent', agent))
            gevent.sleep(0)


    # slightly different semantics, due to the nature of metaagents
    def step_metaagent(self, cell):
        while True:
            stepnum = step_event.get()
            if stepnum == -1:
                # We're done
                return
            for metaagent in self.sim.metaagents:
                metaagent.run(self.sim, cell)
                gevent.sleep(0)
            result_queue.put(('metaagent', cell))



class NetServer(Server):
    """
    Network server, remote UI.
    """
    def loop(self):
        """
        Start server loop
        """

        # accept zmq connections


class CliServer(Server, Cmd):
    """
    Interactive self-contained command line server.
    """

    # This one will have the GUI. Who is responsible for
    # drawing the simulation?
    # For simplicity's sake, let the gui introspect the grid.


class WebServer(Server):
    # a bare minimum gui, supporting grids only (for now)

#    from frontent import heatmap_tk

    def load(self, module):
        super(GuiServer, self).load(module)

#        heatmap_tk.draw_init(self.sim.space, module.__name__)

    def run(self, steps=100):
        log.info("Running simulation %s for %d steps..." %
                 (module.__name__, steps))
        for n in range(steps):
            self.step(n)


class DummyServer(Server):
    """
    Run the simulation for N steps, for testing.
    """
