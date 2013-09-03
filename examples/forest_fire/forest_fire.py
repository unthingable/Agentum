from random import random
import logging

from agentum.model import field
from agentum.simulation import Simulation
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


class ForestCell(Cell):
    state = field.State(default='empty',
                        states=['empty', 'occupied', 'burning'])

    def __str__(self):
        return "%s" % str(self.point)

    def run(self, simulation):
        neighbors = simulation.space.neighbors(self, r=1)

        if self.state == 'burning':
            self.state = 'empty'
        elif self.state == 'occupied':
            if (any(x.state == 'burning' for x in neighbors)
                    or random() < simulation.ignition):
                self.state = 'burning'
        else:
            # Cell is empty
            if random() < simulation.fill:
                self.state = 'occupied'


def setup(simulation):
    # Create space
    simulation.space = CellSpace(ForestCell, dimensions=simulation.dimensions)
    # Create agents - no agents
