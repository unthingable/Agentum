"""
Example simulation setup and agent code that uses the existing spaces.
"""
from itertools import ifilter, cycle
import logging
import sys
import time
from grid import CellSpace, GridSpace
from random import choice

logging.basicConfig()
LOG = logging.getLogger("sim")
LOG.setLevel(logging.DEBUG)

class Simulation(object):
    pass

# To keep things superbly simple, bug and cell are simple containers, no functionality.
class Bug(object):
    __slots__ = "idx", "happiness"
    def __init__(self):
        self.happiness = 0
        self.idx = 0

class BugCell(object):
    __slots__ = "bugs", "heat"
    def __init__(self):
        self.heat = 0
        self.bugs = set()

class Heatbugs(Simulation):
    class properties:
        heat = 1.5          # how much heat the bug emits per turn
        t_max = 2
        t_min = 0.4
        max_bugs_per_cell = 1

    def __init__(self, dimensions=(100,100), numbugs=30):
        self.grid = GridSpace(dimensions=dimensions, cell_fn = BugCell)
        self.bugs = set()
        self.max_heat = 0

        # cheat a little: know some implementation details. This is GridSpace specific.
        # replace for other cellspace
        self.cell_iter_random = cycle(self.grid.cells(CellSpace.tr_random))
        self.available_cell_iter = ifilter(lambda x: self._can_add(*x), self.cell_iter_random)

        # scatter bugs around
        for x in range(numbugs):
            self.add_bug(cell_iter=self.available_cell_iter)

    def _can_add(self, idx=None, cell=None):
        cell = cell or self.grid[idx]
        return len(cell.bugs) < self.properties.max_bugs_per_cell

    def add_bug(self, index=None, bug=None, cell_iter=None):
        """
        Add a single bug to the simulation.
        """
        bug = bug or Bug()
        if bug in self.bugs:
            LOG.warn("Bug %s already added" % bug)
            return False
        if index:
            cell = self.grid[index]
        else:
            cell_iter = cell_iter or self.available_cell_iter
            index, cell = cell_iter.next()

        if self._can_add(index, cell):
            cell.bugs.add(bug)
            self.bugs.add(bug)
            bug.idx = index
            return bug
        else:
            LOG.debug("No more bug vacancies at cell (%s,%s)" % index)
            return False

    def move_bug(self, bug, idx):
        # yay, move
        cell = self.grid[bug.idx]
        new_cell = self.grid[idx]
        new_cell.bugs.add(bug)
        cell.bugs.remove(bug)
        LOG.debug("%s -> %s" % (bug.idx, idx))
        bug.idx = idx
        return bug, idx


    def step_bug(self, bug):
        # emit heat.
        cell = self.grid[bug.idx]
        cell.heat += self.properties.heat
        if cell.heat > self.max_heat:
            self.max_heat = cell.heat
            #LOG.debug("max heat: %s" % cell.heat)

        too_hot = cell.heat > self.properties.t_max
        too_cold = cell.heat < self.properties.t_min
        if too_hot or too_cold:
            # FFFUUUUUuuu!
            bug.happiness -= 1
            # Find a node to migrate to.
            neighbors = self.grid.neighbors(bug.idx)
            for idx, new_cell in sorted(neighbors, key=lambda (k,v): v.heat, reverse=too_cold):
                if self.properties.t_min < new_cell.heat < self.properties.t_max:
                    if self._can_add(cell=new_cell):
                        bug, idx = self.move_bug(bug, idx)
                        break
        else:
            # A bug that does not move is a happier bug.
            bug.happiness += 1

    def diffuse(self):
        """
        Rudimentary heat diffusion.
        Suppose half the lost heat radiates and the other half transmits.
        """
        transmission_coeff = 0.3
        # allow the grid to cool down
        sink_coeff = 0.1
        for idx, cell in self.grid.cells():
            # how much total heat the cell radiates
            emission_loss = cell.heat * transmission_coeff
            neighbors = self.grid.neighbors(idx)
            for nidx,n in neighbors:
                # Only colder cells (positive delta) will absorb the heat.
                # Sum of transmissions cannot be greater that the total emission.
                delta = cell.heat - n.heat
                n.heat += emission_loss / len(neighbors)
            cell.heat -= emission_loss + (cell.heat * sink_coeff)


import drawtk as drawlib
def run_simulation(steps=50, numbugs=20, draw=False, sleep=0):
    s = Heatbugs()
    LOG.info("Starting simulation.")

    drawlib.draw_init(s.grid)

    for step in range(steps):
        LOG.info("Step: %s" % step)
        s.diffuse()
        for bug in s.bugs:
            s.step_bug(bug)
        if draw:
            drawlib.draw_grid(s.grid)
        if sleep:
            time.sleep(sleep)
    LOG.info("Done! Max heat: %s" % s.max_heat)
    return s

if __name__ == "__main__":
    run_simulation()
