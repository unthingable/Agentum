"""
Example simulation setup and agent code that uses the existing spaces.
"""
import logging
import sys
import time
from grid import CellSpace, GridSpace
from operator import attrgetter

HEAT = 1.5
TOLERANCE_MAX = 2
TOLERANCE_MIN = 0.4
MAX_HEAT = 0

class Bug(object):
    __slots__ = "name", "idx", "happiness"
    def __init__(self):
        self.happiness = 0

logging.basicConfig()
LOG = logging.getLogger("sim")
LOG.setLevel(logging.DEBUG)

from random import choice, shuffle
def init_grid(grid, numbugs=20):
    bugs = set()
    numbugs = min(len(grid), numbugs)
    # scatter bugs around
    cells = grid.cells(CellSpace.tr_random)
    while len(bugs) < numbugs:
        idx, cell = cells.next()
        bug = Bug()
        bug.name = len(bugs)
        bug.idx = idx    # backlink
        bugs.add(bug)
        cell.bug = bug
    return bugs


def move_bug(grid, bug, idx):
    # yay, move
    cell = grid[bug.idx]
    new_cell = grid[idx]
    new_cell.bug = bug
    cell.bug = None
    bug.idx = idx
    LOG.debug("%s -> %s" % (bug.name, idx))
    return bug, idx


def step_bug(grid, bug):
    # emit heat.
    cell = grid[bug.idx]
    cell.heat += HEAT
    global MAX_HEAT
    if cell.heat > MAX_HEAT:
        MAX_HEAT = cell.heat
        #LOG.debug("max heat: %s" % cell.heat)

    too_hot = cell.heat > TOLERANCE_MAX
    too_cold = cell.heat < TOLERANCE_MIN
    if too_hot or too_cold:
        # FFFUUUUUuuu!
        bug.happiness -= 1
        # Find a node to migrate to.
        neighbors = grid.neighbors(bug.idx)
        for idx, new_cell in sorted(neighbors, key=lambda (k,v): v.heat, reverse=too_cold):
            if TOLERANCE_MIN < new_cell.heat < TOLERANCE_MAX:
                if not new_cell.bug:
                    bug, idx = move_bug(grid, bug, idx)
                    break
    else:
        # A bug that does not move is a happier bug.
        bug.happiness += 1

def diffuse(grid):
    """
    Rudimentary heat diffusion.
    Suppose half the lost heat radiates and the other half transmits.
    """
    transmission_coeff = 0.3
    # allow the grid to cool down
    sink_coeff = 0.1
    for idx, cell in grid.cells():
        # how much total heat the cell radiates
        emission_loss = cell.heat * transmission_coeff
        neighbors = grid.neighbors(idx)
        for nidx,n in neighbors:
            # Only colder cells (positive delta) will absorb the heat.
            # Sum of transmissions cannot be greater that the total emission.
            delta = cell.heat - n.heat
            n.heat += emission_loss / len(neighbors)
        cell.heat -= emission_loss + (cell.heat * sink_coeff)

class BugCell(object):
    __slots__ = "bug", "heat"
    def __init__(self):
        self.heat = 0
        self.bug = None

import drawtk as drawlib
def run_simulation(steps=50, numbugs=300, draw=False, sleep=0):
    g = GridSpace(cell_fn=BugCell)
    LOG.info("Starting simulation.")
    bugs = init_grid(g, numbugs=numbugs)

    drawlib.draw_init(g)

    for step in range(steps):
        LOG.info("Step: %s" % step)
        diffuse(g)
        for bug in bugs:
            sys.stdout.write('.')
            sys.stdout.flush()
            step_bug(g, bug)
        if draw:
            drawlib.draw_grid(g)
        if sleep:
            time.sleep(sleep)
    LOG.info("Done! Max heat: %s" % MAX_HEAT)
    return g

if __name__ == "__main__":
    run_simulation()
