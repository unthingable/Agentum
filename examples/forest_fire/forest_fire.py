from random import random
import logging

from agentum.simulation import Simulation, Container
from agentum.agent import MetaAgent
from agentum.space import Cell, GridSpace as CellSpace

log = logging.Logger(__name__)

class config(Container):
    ignition = 0.3
    fill = 0.5
    dimensions = (100, 100)


class Forest(MetaAgent):

    def run(self, simulation, cell):
        neighbors = simulation.space.neighbors(cell, r=1)

        if cell.state == 'burning':
            cell.state = 'empty'
        elif cell.state == 'occupied':
            if any(x.state == 'burning' for x in neighbors):
                cell.state = 'burning'
            if not cell.state == 'burning' and random() < config.ignition:
                cell.state == 'burning'
        else:
            # Cell is empty
            if random() < config.fill:
                cell.state = 'occupied'

class ForestCell:
    states = ['empty', 'occupied', 'burning']
    _state = 'empty'

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        log.debug("Cell %r %s" % (self, state))
        self._state = state

def setup(simulation):
    # Create space
    simulation.space = CellSpace(ForestCell, dimensions=config.dimensions)
    # Create agents
    simulation.metaagents.append(Forest())
