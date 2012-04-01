"""
Example simulation setup and agent code that uses the existing spaces.
"""
import logging
import sys
from grid import CellSpace, GridSpace
from operator import attrgetter

HEAT = 0.3
TOLERANCE = 2
MAX_HEAT = 0

class Bug(object):
    __slots__ = "name", "idx"

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

def step_bug(grid, bug):
    # emit heat.
    cell = grid[bug.idx]
    cell.heat += HEAT
    global MAX_HEAT
    if cell.heat > MAX_HEAT:
        MAX_HEAT = cell.heat
        #LOG.debug("max heat: %s" % cell.heat)
    if cell.heat > TOLERANCE:
        # FFFUUUUUuuu!. Find a node to migrate to.
        neighbors = grid.neighbors(bug.idx)
        for idx, new_cell in sorted(neighbors, key=lambda (k,v): v.heat):
            if not new_cell.bug:
                # yay, move
                new_cell.bug = bug
                cell.bug = None
                bug.idx = idx
                # cheat a little. TODO: give nodes __unicode__()
                LOG.debug("%s -> %s" % (bug.name, idx))
                break

def diffuse(grid):
    """
    Rudimentary heat diffusion.
    """
    cardinality = len(grid.dimensions)
    heat_distribution_coeff = 2 ** cardinality
    heat_loss = 0.1
    for idx, cell in grid.cells():
        heat_gain = (cell.heat * heat_loss) / heat_distribution_coeff
        for idx,n in grid.neighbors(idx):
            n.heat += heat_gain
        cell.heat *= 1 - heat_loss

class BugCell(object):
    __slots__ = "bug", "heat"
    def __init__(self):
        self.heat = 0
        self.bug = None

def run_simulation(steps=50):
    g = GridSpace(cell_fn=BugCell)
    LOG.info("Starting simulation.")
    bugs = init_grid(g)
    for step in range(steps):
        LOG.info("Step: %s" % step)
        for bug in bugs:
            sys.stdout.write('.')
            sys.stdout.flush()
            step_bug(g, bug)
        diffuse(g)
    LOG.info("Done! Max heat: %s" % MAX_HEAT)
    return g

if __name__ == "__main__":
    run_simulation()