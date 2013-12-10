from collections import defaultdict, Counter
from itertools import chain
from random import shuffle

from colorama import Fore

from agentum.simulation import Simulation
from agentum.space import CellSpace, GridSpace, Cell
from agentum.agent import Agent
from agentum.model import field
from agentum.model.field import Integer as I, Float as F, UFloat as UF
#from agentum.utils import adict


class Patch(Cell):
    ratios = defaultdict(lambda: 1)

    def update_ratios(self, sim):
        hood = sim.space.neighbors(self, r=1)
        total_neighbors = 0
        totals = defaultdict(int)
        # totals = Counter()
        hood = list(chain(hood, [self]))
        for cell in hood:
            total_neighbors += len(cell.agents)
            for resident in cell.agents:
                totals[resident.color] += 1
            # Counter seems slower:
            # totals.update(resident.color for resident in cell.agents)
        for color in totals:
            # negative ratio of friends among neighbors
            ratio = float(total_neighbors - (totals[color] - 1)) / total_neighbors
            self.ratios[color] = ratio


class Turtle(Agent):
    '''
    Call it what you will.
    '''
    # happiness = field.Float(1)
    color = None

    def move(self, sim, force=False):
        home = sim.space.find(self)
        new_home = None
        tolerance = sim.agent_params[self.color]['tolerance']
        if force or home.ratios[self.color] > tolerance:
            # gotta move!
            new_home = next(x for x in sim.space.cells(CellSpace.tr_random) if not x.agents)
            # for cell in sim.space.cells(CellSpace.tr_random):
            #     if (force or cell.ratios[self.color] > tolerance) and not cell.agents:
            #         # this is good, I'll move
            #         new_home = cell
            #         break
            if new_home:
                sim.space.move(self, new_home)
            else:
                # dear facebook, I'm sooo unhappy
                print '%s wanted to move but could not' % self.id()
        # for manual placement
        return new_home


class Schelling(Simulation):
    '''
    Schelling segregation model
    '''
    dimensions = field.List(field.Integer, (20, 40))
    agent_params = {'red': {'fill': 0.4, 'tolerance': 0.4},
                    'blue': {'fill': 0.4, 'tolerance': 0.4}}

    def setup(self):
        self.space = GridSpace(Patch, dimensions=self.dimensions)
        total = self.dimensions[0] * self.dimensions[1]

        # seed the board randomly
        for color, params in self.agent_params.iteritems():
            for n in xrange(int(total * params['fill'])):
                agent = Turtle()
                agent.color = color
                # Force the agent to move to a new random cell
                if agent.move(self, force=True):
                    self.agents.append(agent)
                else:
                    raise Exception("Could not move in a new agent: pond is full")

        self.update_fig()
        self.steps = ((Patch.update_ratios, (Turtle.move, self.shuffled_turtles)))

    def shuffled_turtles(self):
        '''
        Ensure random ordering of agents
        '''
        agents = list(self.agents)
        shuffle(agents)
        return agents

    def dump(self):
        colormap = {'b': Fore.BLUE + 'o', 'r': Fore.RED + 'o'}

        def formatter(cell):
            if len(cell.agents) > 1:
                return '+'
            elif cell.agents:
                return colormap[cell.agents.copy().pop().color[0]] + Fore.RESET
            else:
                return ' '
        matrix = self.space.bbox(func=formatter)
        return '\n'.join(''.join(x) for x in matrix)

    def update_fig(self):
        from matplotlib import pyplot as plt
        from matplotlib import transforms
        if not hasattr(self, 'fig'):
            plt.axis('off')
            self.fig = plt.figure()
            self.plt = self.fig.add_subplot(111,
                                            axisbg='k',
                                            aspect='equal')

        offset = transforms.offset_copy(self.plt.transData,
                                        x=5, y=5, units='dots')

        # bucket patches
        buckets = {'b': [],
                   'r': []}

        for cell in self.space.cells():
            if cell.agents:
                buckets[cell.agents.copy().pop().color[0]].append(cell.point)

        self.plt.clear()
        for b, points in buckets.items():
            self.plt.plot(*zip(*points), marker='o',
                          markerfacecolor=b,
                          linestyle='None',
                          markersize=8,
                          transform=offset)
        # plt.draw()

    def draw(self):
        self.update_fig()
        self.fig.show()


if __name__ == '__main__':
    from agentum.worker import WorkerSerial as Worker
    import enaml
    from enaml.qt.qt_application import QtApplication

    with enaml.imports():
        from schelling_view import SchellingView

    from agentum import protocol
    protocol.push = lambda x: None

    w = Worker(Schelling)
    w.sim_init()

    app = QtApplication()
    view = SchellingView(worker=w)
    view.show()

    app.start()
