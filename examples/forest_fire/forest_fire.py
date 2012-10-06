from random import random
import logging

from agentum.simulation import Simulation
from agentum.agent import MetaAgent
from agentum.space import Cell, GridSpace as CellSpace

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# class config(Container):
#     ignition = 0.3
#     fill = 0.5
#     dimensions = (100, 100)


class ForestFire(Simulation):
    ignition = 0.3
    fill = 0.5
    dimensions = (100, 100)

    inputs = ['ignition', 'fill']
    outputs = ['dimensions']

simulation = ForestFire


class Forest(MetaAgent):

    def run(self, simulation, cell):
        neighbors = simulation.space.neighbors(cell, r=1)

        if cell.state == 'burning':
            cell.state = 'empty'
        elif cell.state == 'occupied':
            if any(x.state == 'burning' for x in neighbors):
                cell.state = 'burning'
            if not cell.state == 'burning' and random() < simulation.ignition:
                cell.state == 'burning'
        else:
            # Cell is empty
            if random() < simulation.fill:
                cell.state = 'occupied'


class ForestCell(Cell):
    states = ['empty', 'occupied', 'burning']
    _state = 'empty'
    state_num = 0

    outputs = ['state_num']

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        # log.debug("Cell %s: %s" % (self, new_state))
        self._state = new_state
        self.state_num = self.states.index(new_state)

    def __str__(self):
        return "%s" % str(self.point)


def setup(simulation):
    # Create space
    simulation.space = CellSpace(ForestCell, dimensions=simulation.dimensions)
    # Create agents
    simulation.metaagents.append(Forest())
