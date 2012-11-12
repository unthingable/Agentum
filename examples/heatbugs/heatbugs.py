from itertools import izip, ifilter, cycle
from random import random
import logging

from agentum.simulation import Simulation
from agentum.agent import Agent, MetaAgent
from agentum.space import Cell, GridSpace as CellSpace
from agentum import settings

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(settings.LOGLEVEL)


class HeatBugs(Simulation):
    dimensions = (100, 100)
    numbugs = 30

    heat = 1.5          # how much heat a bug emits per turn
    t_max = 2           # how much can the bug tolerate
    t_min = 0.4

    transmission = 0.3  # how much heat is radiated to neighbors
    sink = 0.1          # how much heat is lost into space

    # runtime stuff
    max_heat = 0    # maximum heat observed

    inputs = 'heat t_max t_min transmission sink'.split()

simulation = HeatBugs


# A cell can be anything: a dict, a list, an object, etc..
# Here we use slots as an example of compact storage.
class BugCell(Cell):
    __slots__ = "bugs", "heat"
    outputs = ['heat']

    def __init__(self, point):
        # more elegant way to do this?
        Cell.__init__(self, point)
        self.heat = 0
        self.bugs = set()


class Bug(Agent):
    happiness = 0
    cell = None

    outputs = ['cell']
    # add defaults?

    def run(self, simulation):
        cell = simulation.space.find(self)
        cell.heat += simulation.heat
        if cell.heat > simulation.max_heat:
            simulation.max_heat = cell.heat

        too_hot = cell.heat > simulation.t_max
        too_cold = cell.heat < simulation.t_min
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
                     (too_cold and new_cell.heat > cell.heat))):
                    # Yay!
                    self.move(simulation, new_cell)
                    break
            else:
                log.debug("Bug %s could not move" % self)

        else:
            # A bug that does not move is a happier bug.
            self.happiness += 1

    def move(self, simulation, new_cell):
        self.cell = new_cell.id()
        simulation.space.move(self, new_cell)

class Dissipator(MetaAgent):
    def run(self, simulation, cell):
        emission_loss = cell.heat * simulation.transmission
        neighbors = simulation.space.neighbors(cell, r=1)
        for n in neighbors:
            # Only colder cells (positive delta) will absorb the heat.
            # Sum of transmissions cannot be greater that the total emission.
            delta = cell.heat - n.heat
            n.heat += emission_loss / len(neighbors)
        cell.heat -= emission_loss + (cell.heat * simulation.sink)


def setup(simulation):
    # Create space
    simulation.space = CellSpace(BugCell, dimensions=simulation.dimensions)
    # Create agents
    # ... for now the hard way.
    # Must add them in both the simulation and the space...
    cell_iter = cycle(simulation.space.cells(CellSpace.tr_random))
    unoccupied_cell_iter = (x for x in cell_iter if not x.bugs)

    # Randomly scatter the bugs around the space
    simulation.metaagents.append(Dissipator())
    for n, cell in izip(range(simulation.numbugs), unoccupied_cell_iter):
        bug = Bug()
        log.debug("Adding agent %r" % bug)
        simulation.space.add_agent(bug, cell)
        simulation.agents.append(bug)
