"""
Example simulation setup and agent code that uses the existing spaces.
"""
import logging
import sys
from grid import CellSpace, GridSpace
from operator import attrgetter

HEAT = 1.1
TOLERANCE = 2

class Bug(object):
    __slots__ = "name", "cell"

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
        bug.cell = cell    # backlink
        bugs.add(bug)
        cell.bug = bug
    return bugs

def step_bug(grid, bug):
    # emit heat.
    cell = bug.cell
    cell.heat += HEAT
    if cell.heat > TOLERANCE:
        # FFFUUUUUuuu!. Find a node to migrate to.
        neighbors = grid.neighbors(bug.node)
        for idx, new_cell in sorted(neighbors, key=lambda k,v: v['heat']):
            if not new_cell.bug:
                # yay, move
                new_cell.bug = bug
                cell.bug = None
                bug.cell = new_cell
                # cheat a little. TODO: give nodes __unicode__()
                LOG.debug("%s: %s -> %s" % (bug.name,
                    grid.inverted_node_map[cell],
                    grid.inverted_node_map[new_cell]))
                break

def diffuse(grid):
    """
    Rudimentary heat diffusion.
    """
    cardinality = len(grid.dimensions)
    heat_distribution_coeff = 2 ** cardinality
    heat_loss = 0.2
    for idx, cell in grid.cells():
        heat_gain = (cell.heat * heat_loss) / heat_distribution_coeff
        for n in grid.neighbors(cell):
            n.heat += heat_gain
        cell.heat *= 1 - heat_loss

class BugCell(object):
    __slots__ = "bug", "heat"
    def __init__(self):
        self.heat = 0

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
    LOG.info("Done!")
    return g
