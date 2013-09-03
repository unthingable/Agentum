"""
NOTE: gevent is slower (a lot!) when running on a VM:
http://stackoverflow.com/questions/10656953/redis-gevent-poor-performance-what-am-i-doing-wrong
"""

import logging
import gevent
from gevent.event import AsyncResult
from gevent.pool import Group
import imp
import os

from agentum import protocol, settings

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(settings.LOGLEVEL)

step_event = AsyncResult()
# result_queue = Queue()


def zrange(x):
    '''
    Like xrange, but go on forever if x is 0 (or None)
    '''
    x = x or -1
    y = 0
    while x != y:
        yield y
        y += 1


def fpass(*x):
    'Dummy function'
    pass


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


class WorkerBase(object):

    # clients = []
    # simulations = []
    # running_simulations = []

    # For now, a single simulation, no clients
    sim = None
    module = None

    _num_cells = 0
    stepnum = 0

    def load(self, module):
        self.module = module
        self.sim = module.simulation()

        # Call the setup() methods, if any
        getattr(module, 'setup', fpass)(self.sim)
        getattr(self.sim, 'setup', fpass)()

        log.info("Loading simulation %s" % module.__name__)

        # protocol.active = False
        protocol.active = True
        protocol.greet()

        # dirty hack to test the concept:

        protocol.send('sim name %s' % module.__name__)
        if self.sim.__doc__:
            protocol.send(['sim', 'doc', self.sim.__doc__])
        if self.sim.space:
            protocol.send('sim space grid'.split() +
                          [self.sim.space.dimensions],
                          )
        protocol.flush(lambda x: ['preamble', x])
        # simulations.append(sim)
        # ...

    def run(self, steps=100):
        """
        Run the simulation for N steps. Set to 0 to run endlessly.
        """
        log.info("Running simulation %s for %d steps..." %
                 (self.module.__name__, steps))
        for n in zrange(steps):
            # TODO: get messages and stop if requested, otherwise:
            self.step(flush=False)
        protocol.flush(lambda x: ['frame', self.stepnum, x])

    def step_agent(self, agent):
        agent.run(self.sim)


class WorkerSerial(WorkerBase):

    def step(self, flush=True):
        self.stepnum += 1
        log.debug("Step: %d" % self.stepnum)
        # protocol.send(("step", self.stepnum))
        sim = self.sim

        sim.before_step(self.stepnum)
        # Run agents
        map(self.step_agent, sim.agents)
        # Run metaagents
        # protocol.active = False
        if sim.space:
            for cell in sim.space.cells():
                cell.run(self.sim)
        # protocol.active = True
        # for cell in self.sim.space.cells():
        #     cell.__fire__()
        # Instead:
        sim.after_step(self.stepnum)
        if flush:
            protocol.flush(lambda x: ['frame', self.stepnum, x])


# Update before using again...
class WorkerGevent(WorkerBase):
    group = None

    def step(self):
        self.stepnum += 1
        log.debug("Step: %d" % self.stepnum)
        sim = self.sim

        if not self.group:
            self.group = Group()

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


def load_sim(simmodule, worker=WorkerSerial):
    module = load_module(simmodule)
    w = worker()
    w.load(module)
    return w


# class WorkerGevent2(WorkerBase):

#     def run(self, steps=100):
#         """
#         Run the simulation for N steps. Set to 0 to run endlessly.
#         """
#         agent_group = Group()
#         magent_group = Group()
#         log.info("Running simulation %s for %d steps..." %
#                  (self.module.__name__, steps))

#         # Gentlemen, start your agents
#         for agent in self.sim.agents:
#             agent_group.add(gevent.spawn(self.step_agent, agent))
#         for cell in self.sim.space.cells():
#             magent_group.add(gevent.spawn(self.step_metaagent, cell))

#         # TODO: remove
#         self._num_cells = len(self.sim.space.cells())

#         for n in zrange(steps):
#             # TODO: get messages and stop if requested, otherwise:
#             self.step(n)
#         # Finally:
#         step_event.set(-1)

#         # Check agents for errors?
#         agent_group.join()
#         magent_group.join()

#     def step(self, stepnum=-1):
#         log.debug("Step: %d" % stepnum)

#         if not step_event.ready():
#             step_event.set(stepnum)

#         # Wait for agents to do their thing
#         finished = {'agent': set(), 'metaagent': set()}
#         while True:
#             if (len(finished['agent']) == len(self.sim.agents) and
#                 len(finished['metaagent']) == self._num_cells):
#                 break
#             (stream, item) = result_queue.get()
#             finished[stream].add(item)

#     def step_agent(self, agent):
#         while True:
#             stepnum = step_event.get()
#             if stepnum == -1:
#                 # We're done
#                 return
#             agent.run(self.sim)
#             # Report we're done with the step
#             result_queue.put(('agent', agent))
#             gevent.sleep(0)


#     # slightly different semantics, due to the nature of metaagents
#     def step_metaagent(self, cell):
#         while True:
#             stepnum = step_event.get()
#             if stepnum == -1:
#                 # We're done
#                 return
#             for metaagent in self.sim.metaagents:
#                 metaagent.run(self.sim, cell)
#                 gevent.sleep(0)
#             result_queue.put(('metaagent', cell))
