"""
Example simulation setup and agent code that uses the existing spaces.
"""
import logging
import sys
import time
from grid import CellSpace, GridSpace
from operator import attrgetter

HEAT = 1.3
TOLERANCE = 2
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

def step_bug(grid, bug):
    # emit heat.
    cell = grid[bug.idx]
    cell.heat += HEAT
    global MAX_HEAT
    if cell.heat > MAX_HEAT:
        MAX_HEAT = cell.heat
        #LOG.debug("max heat: %s" % cell.heat)
    if cell.heat > TOLERANCE:
        # FFFUUUUUuuu!
        bug.happiness -= 1
        # Find a node to migrate to.
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
    else:
        # A bug that does not move is a happier bug.
        bug.happiness += 1

def diffuse(grid):
    """
    Rudimentary heat diffusion.
    Suppose half the lost heat radiates and the other half transmits.
    """
    radiation_loss_coeff = 0.001
    transmission_coeff = 0.2
    for idx, cell in grid.cells():
        neighbors = grid.neighbors(idx)
        transmission_loss = cell.heat * transmission_coeff
        for idx,n in neighbors:
            n.heat += transmission_loss / len(neighbors)
        cell.heat -= (cell.heat * radiation_loss_coeff) + transmission_loss

class BugCell(object):
    __slots__ = "bug", "heat"
    def __init__(self):
        self.heat = 0
        self.bug = None

import draw as drawlib
def run_simulation(steps=50, draw=False, sleep=0):
    g = GridSpace(cell_fn=BugCell)
    LOG.info("Starting simulation.")
    bugs = init_grid(g)
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