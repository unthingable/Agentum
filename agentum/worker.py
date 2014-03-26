"""
NOTE: gevent is slower (a lot!) when running on a VM:
http://stackoverflow.com/questions/10656953/redis-gevent-poor-performance-what-am-i-doing-wrong
"""

from collections import defaultdict
import logging
# import gevent
# from gevent.event import AsyncResult
# from gevent.pool import Group
import imp
import inspect
from functools import wraps
from itertools import ifilter
import os
import sys

from atom.api import Atom, Int

from agentum import protocol, settings
from agentum.simulation import Simulation
from agentum.agent import Agent
from agentum.space import Cell
from agentum.model import Atomizer

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(settings.LOGLEVEL)

# step_event = AsyncResult()
# result_queue = Queue()


def execute_and_watch(meth):
    @wraps(meth)
    def wrapper(self, *args, **kw):
        try:
            return meth(self, *args, **kw)
        except Exception, e:
            protocol.send(['ERROR', str(e)], compress=False)
            raise
    return wrapper


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


def find_sim(simmodule):
    """
    simmodule: pathname string
    """
    if os.path.isfile(simmodule):
        dirname, module_name = os.path.split(simmodule)
        module_name = module_name.replace('.py', '')
        module = imp.load_source(module_name,
                                 simmodule.replace('.pyc', '.py'))
    else:
        raise Exception("Not a file: %s" % simmodule)
    for attr in dir(module):
        attr = getattr(module, attr)
        log.debug("trying %s", attr)
        if inspect.isclass(attr) and issubclass(attr, Simulation) and attr != Simulation:
            return attr
    raise Exception("Simulation not found in module %s", simmodule)


class WorkerBase(Atomizer):

    # clients = []
    # simulations = []
    # running_simulations = []

    # For now, a single simulation, no clients
    stepnum = Int()

    def __init__(self, simclass, simmodule=None):
        self.is_setup = False

        self.module = simmodule or sys.modules[simclass.__module__].__file__
        self.simclass = simclass
        self.sim = simclass()

        log.info("Loading simulation %s" % simclass.__name__)

        # protocol.active = False
        protocol.active = True
        protocol.greet()

        # dirty hack to test the concept:

        protocol.send('sim name %s' % simclass.__name__)
        if simclass.__doc__:
            protocol.send(['sim', 'doc', simclass.__doc__])
        protocol.flush(lambda x: ['preamble', x])
        # simulations.append(sim)
        # ...

    @execute_and_watch
    def sim_init(self, force=False):
        if force or not self.is_setup:
            self.sim.__init__()
            self.sim.setup()
            self.is_setup = True
            self.steppables = {}
            self.steps = []
            self.stepnum = 0

            # initialize steps
            if not self.sim.steps:
                raise Exception("Must specify simulation steps")
            else:
                for step in self.sim.steps:
                    if isinstance(step, (list, tuple)):
                        step, iterfun = step
                    else:
                        if inspect.ismethod(step) and step.im_self is not None:
                            # a bounded method
                            self.steppables[step.im_class] = [step.im_self].__iter__
                            self.steps.append(step)
                            continue
                            # raise Exception("Only unbounded methods can be steps")
                        if issubclass(step.im_class, Agent):
                            # multiple agent types supported, step() will filter
                            iterfun = self.sim.agents.__iter__
                        elif issubclass(step.im_class, Cell):
                            iterfun = self.sim.space.cells
                        else:
                            raise Exception('Unknown step class, must provide an iterator')
                    self.steppables[step.im_class] = iterfun
                    self.steps.append(step)
                log.debug("Steps: %s", self.steps)

            if self.sim.space:
                protocol.send('sim space grid'.split() +
                              [self.sim.space.dimensions],
                              )
            protocol.flush(lambda x: ['preamble', x])

    @execute_and_watch
    def run(self, steps=100):
        """
        Run the simulation for N steps. Set to 0 to run endlessly.
        """
        self.sim_init()
        log.info("Running simulation %s for %d steps..." %
                 (self.sim.__class__.__name__, steps))
        for n in zrange(steps):
            # TODO: get messages and stop if requested, otherwise:
            self.step(flush=False)
        protocol.flush(lambda x: ['frame', self.stepnum, x])

    def reload(self):
        'Reload the entire simulation'
        newsim = find_sim(self.module)
        self.is_setup = False
        self.__init__(newsim, self.module)
        self.sim_init()


class WorkerSerial(WorkerBase):

    @execute_and_watch
    def step(self, flush=True):
        self.sim_init()

        self.stepnum += 1
        log.debug("Step: %d" % self.stepnum)
        # protocol.send(("step", self.stepnum))
        sim = self.sim

        sim.before_step(self.stepnum)

        for step_method in self.steps:
            log.debug('calling steppable %r' % step_method)
            for steppable in self.steppables[step_method.im_class]():
                # log.debug('calling %r on %r' % (step_method, steppable))
                if step_method.im_self is not None:
                    if isinstance(step_method.im_self, sim.__class__):
                        step_method()
                    else:
                        step_method(sim)
                elif isinstance(steppable, step_method.im_class):
                    step_method(steppable, sim)

        sim.after_step(self.stepnum)
        if flush:
            protocol.flush(lambda x: ['frame', self.stepnum, x])


# # Update before using again...
# class WorkerGevent(WorkerBase):
#     group = None

#     def step(self):
#         self.stepnum += 1
#         log.debug("Step: %d" % self.stepnum)
#         sim = self.sim

#         if not self.group:
#             self.group = Group()

#         # Run agents
#         self.group.imap(self.step_agent, sim.agents)
#         # Run metaagents
#         self.group.imap(self.step_metaagent, sim.space.cells())
#         # This is a good place to emit state updates and such

#     def step_agent(self, agent):
#         agent.run(self.sim)
#         gevent.sleep(0)

#     # slightly different semantics, due to the nature of metaagents
#     def step_metaagent(self, cell):
#         for metaagent in self.sim.metaagents:
#             metaagent.run(self.sim, cell)
#             gevent.sleep(0)


def load_sim(simmodule, worker=WorkerSerial):
    sim = find_sim(simmodule)
    return worker(sim, simmodule)


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
