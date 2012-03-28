"""
Example simulation setup and agent code that uses the existing spaces.
"""
#import Tkinter
#import grid
import logging
import sys
from grid import CellSpace, Grid
from operator import attrgetter

class Agent(object):
    pass

HEAT = 1.1
TOLERANCE = 2

class Bug(Agent):
    __slots__ = "name", "cell"

#grid = new Grid()

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
        cell = cells.next()
        bug = Bug()
        bug.name = len(bugs)
        bug.cell = cell    # backlink
        bugs.add(bug)
        cell.bug = bug
    return bugs

def step_bug(grid, bug):
    # emit heat.
    cell = bug.cell
    cell.heat += HEAT
    if cell.heat > TOLERANCE:
        # FFFUUUUUuuu!. Find a cell to migrate to.
        neighbors = grid.neighbors(bug.cell)
        for new_cell in sorted(neighbors, key=attrgetter("heat")):
            if not new_cell.bug:
                # yay, move
                new_cell.bug = bug
                cell.bug = None
                bug.cell = new_cell
                # cheat a little. TODO: give cells __unicode__()
                LOG.debug("%s: %s -> %s" % (bug.name,
                    grid.inverted_cell_map[cell],
                    grid.inverted_cell_map[new_cell]))
                break

def diffuse(grid):
    """
    Rudimentary heat diffusion.
    """
    cardinality = len(grid.dimensions)
    heat_distribution_coeff = 2 ** cardinality
    heat_loss = 0.2
    for cell in grid.cells():
        heat_gain = (cell.heat * heat_loss) / heat_distribution_coeff
        for n in grid.neighbors(cell):
            n.heat += heat_gain
        cell.heat *= 1 - heat_loss

def run_simulation(steps=50):
    g = Grid()
    LOG.info("Starting simulation.")
    bugs = init_grid(g)
    for step in range(steps):
        LOG.info("Step: %s" % step)
        for bug in bugs:
            sys.stdout.write('.')
            sys.stdout.flush()
            step_bug(g, bug)
        diffuse(g)
    LOG.info("Done!")
    return g

def draw(g):
    pass
