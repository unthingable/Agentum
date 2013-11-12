from collections import defaultdict
from itertools import chain
from random import shuffle

from agentum.simulation import Simulation
from agentum.space import CellSpace, GridSpace, Cell
from agentum.agent import Agent
from agentum.model import field
from agentum.model.field import Integer as I, Float as F, UFloat as UF
#from agentum.utils import adict


class Patch(Cell):
    ratios = field.Field(defaultdict(lambda: 1))

    def update_ratios(self, sim):
        hood = sim.space.neighbors(self, r=1)
        total_neighbors = 0
        totals = defaultdict(int)
        for cell in chain(hood, [self]):
            total_neighbors += len(cell.agents)
            for resident in cell.agents:
                totals[resident.color] += 1
        for color in totals:
            ratio = float(total_neighbors - totals[color]) / total_neighbors
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
            for cell in sim.space.cells(CellSpace.tr_random):
                if (force or cell.ratios[self.color] > tolerance) and not cell.agents:
                    # this is good, I'll move
                    new_home = cell
                    break
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
    agent_params = field.Field({'red': {'fill': 0.1, 'tolerance': 0.1},
                               'blue': {'fill': 0.4, 'tolerance': 0.1}})

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

        self.steps = ((Patch.update_ratios, (Turtle.move, self.shuffled_turtles)))

    def shuffled_turtles(self):
        '''
        Ensure random ordering of agents
        '''
        agents = list(self.agents)
        shuffle(agents)
        return agents

    def dump(self):
        def formatter(cell):
            if len(cell.agents) > 1:
                return '+'
            elif cell.agents:
                return cell.agents.copy().pop().color[0]
            else:
                return ' '
        matrix = self.space.bbox(func=formatter)
        return '\n'.join(''.join(x) for x in matrix)
