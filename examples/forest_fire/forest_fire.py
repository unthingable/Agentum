from random import random
import logging

from agentum.model import field
from agentum.simulation import Simulation
from agentum.space import Cell, GridSpace as CellSpace
from agentum import settings

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(settings.LOGLEVEL)


class ForestCell(Cell):
    state = field.State(default='empty',
                        states=['empty', 'occupied', 'burning'])

    def __str__(self):
        return "%s" % str(self.point)

    def step(self):
        neighbors = self.sim.space.neighbors(self, r=1)

        if self.state == 'burning':
            self.state = 'empty'
        elif self.state == 'occupied':
            if (any(x.state == 'burning' for x in neighbors)
                    or random() < self.sim.ignition):
                self.state = 'burning'
        else:
            # Cell is empty
            if random() < self.sim.fill:
                self.state = 'occupied'


class ForestFire(Simulation):
    ignition = field.Float(0.3)
    fill = field.Float(0.5)
    dimensions = field.Field((3, 3))

    def setup(self):
        def cell_fn(coordinates):
            cell = ForestCell(coordinates)
            cell.sim = self
            return cell

        self.space = CellSpace(cell_fn, dimensions=self.dimensions)
        self.steps = (ForestCell.step,)
