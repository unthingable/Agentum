from random import random
import logging

from agentum.model import field
from agentum.simulation import Simulation
from agentum.agent import MetaAgent
from agentum.space import Cell, GridSpace as CellSpace
from agentum import settings

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(settings.LOGLEVEL)


class ForestFire(Simulation):
    ignition = field.Float(0.3)
    fill = field.Float(0.5)
    dimensions = field.Field((3, 3))

simulation = ForestFire


class Forest(MetaAgent):

    def run(self, simulation, cell):
        neighbors = simulation.space.neighbors(cell, r=1)

        if cell.state == 'burning':
            cell.state = 'empty'
        elif cell.state == 'occupied':
            if (any(x.state == 'burning' for x in neighbors)
                    or random() < simulation.ignition):
                cell.state = 'burning'
        else:
            # Cell is empty
            if random() < simulation.fill:
                cell.state = 'occupied'


class ForestCell(Cell):
    state = field.State(default='empty',
                        states=['empty', 'occupied', 'burning'])

    def __str__(self):
        return "%s" % str(self.point)


def setup(simulation):
    # Create space
    simulation.space = CellSpace(ForestCell, dimensions=simulation.dimensions)
    # Create agents
    simulation.metaagents.append(Forest())
