from itertools import izip, ifilter, cycle
from random import random
import logging

from agentum.simulation import Simulation, Container
from agentum.agent import Agent, MetaAgent
from agentum.space import Cell, GridSpace as CellSpace

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class config(Container):
    dimensions = (100, 100)
    numbugs = 30

    heat = 1.5          # how much heat a bug emits per turn
    t_max = 2
    t_min = 0.4

    transmission = 0.3  # how much heat transmits
    sink = 0.1          # how much heat is lost into space

    # runtime stuff
    max_heat = 0    # maximum heat observed


# A cell can be anything: a dict, a list, an object, etc..
# Here we use slots as an example of compact storage.
class Cell(object):
    __slots__ = "bugs", "heat", "point"
    def __init__(self):
        self.heat = 0
        self.bugs = set()


class Bug(Agent):
    happiness = 0

    def run(self, simulation):
        cell = simulation.space.find(self)
        cell.heat += config.heat
        if cell.heat > config.max_heat:
            config.max_heat = cell.heat

        too_hot = cell.heat > config.t_max
        too_cold = cell.heat < config.t_min
        if too_hot or too_cold:
            # FFFUUUUUuuu!
            self.happiness -= 1

            # Find a cell to migrate to.
            neighbors = simulation.space.neighbors(cell)
            for new_cell in sorted(neighbors,
                                   key=lambda (v): v.heat,
                                   reverse=too_cold):
                if (not new_cell.bugs and
                    # Is the new cell any better?
                    ((too_hot and new_cell.heat < cell.heat) or
                     (too_cold and new_cell.heat > cell.heat))
                    ):
                    # Yay!
                    simulation.space.move(self, new_cell)
                    break
            else:
                log.debug("Bug %s could not move" % self)

        else:
            # A bug that does not move is a happier bug.
            self.happiness += 1

class Dissipator(MetaAgent):
    def run(self, simulation, cell):
        emission_loss = cell.heat * config.transmission_coeff
        neighbors = simulation.space.neighbors(cell)
        for n in neighbors:
            # Only colder cells (positive delta) will absorb the heat.
            # Sum of transmissions cannot be greater that the total emission.
            delta = cell.heat - n.heat
            n.heat += emission_loss / len(neighbors)
        cell.heat -= emission_loss + (cell.heat * config.sink_coeff)

def setup(simulation):
    # Create space
    simulation.space = CellSpace(Cell, dimensions=config.dimensions)
    # Create agents
    # ... for now the hard way. Must add them in both the simulation and the space...
    cell_iter = cycle(simulation.space.cells(CellSpace.tr_random))
    unoccupied_cell_iter = (x for x in cell_iter if not x.bugs)

    # Randomly scatter the bugs around the space
    for n, cell in izip(range(config.numbugs), unoccupied_cell_iter):
        bug = Bug()
        log.debug("Adding agent %r" % bug)
        simulation.space.add_agent(bug, cell)
        simulation.agents.append(bug)
