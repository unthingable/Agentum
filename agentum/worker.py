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
from agentum import protocol

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


class WorkerBase(object):

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

        # protocol.active = False
        self.sim = module.simulation()
        setup(self.sim)
        # protocol.active = True

        # simulations.append(sim)
        # ...

    def step_agent(self, agent):
        agent.run(self.sim)

    # slightly different semantics, due to the nature of metaagents
    def step_metaagent(self, cell):
        for metaagent in self.sim.metaagents:
            metaagent.run(self.sim, cell)


class WorkerSerial(WorkerBase):
    def run(self, steps=100):
        """
        Run the simulation for N steps. Set to 0 to run endlessly.
        """
        log.info("Running simulation %s for %d steps..." %
                 (self.module.__name__, steps))
        for n in zrange(steps):
            # TODO: get messages and stop if requested, otherwise:
            self.step(n)

    def step(self, stepnum=-1):
        log.debug("Step: %d" % stepnum)
        sim = self.sim

        # Run agents
        map(self.step_agent, sim.agents)
        # Run metaagents
        map(self.step_metaagent, sim.space.cells())
        # This is a good place to emit state updates and such


class WorkerGevent(WorkerBase):
    def run(self, steps=100):
        """
        Run the simulation for N steps. Set to 0 to run endlessly.
        """
        self.group = Group()
        log.info("Running simulation %s for %d steps..." %
                 (self.module.__name__, steps))
        for n in zrange(steps):
            # TODO: get messages and stop if requested, otherwise:
            self.step(n)

    def step(self, stepnum=-1):
        log.debug("Step: %d" % stepnum)
        sim = self.sim

        # Run agents
        self.group.imap(self.step_agent, sim.agents)
        # Run metaagents
        self.group.imap(self.step_metaagent, sim.space.cells())
        # This is a good place to emit state updates and such

    def step_agent(self, agent):
        agent.run(self.sim)
        gevent.sleep(0)


    # slightly different semantics, due to the nature of metaagents
    def step_metaagent(self, cell):
        for metaagent in self.sim.metaagents:
            metaagent.run(self.sim, cell)
            gevent.sleep(0)


class WorkerGevent2(WorkerBase):

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