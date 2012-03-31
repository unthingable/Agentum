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
    __slots__ = "name", "node"

logging.basicConfig()
LOG = logging.getLogger("sim")
LOG.setLevel(logging.DEBUG)

from random import choice, shuffle
def init_grid(grid, numbugs=20):
    bugs = set()
    numbugs = min(len(grid), numbugs)
    # scatter bugs around
    nodes = grid.cells(CellSpace.tr_random)
    while len(bugs) < numbugs:
        node = nodes.next()
        bug = Bug()
        bug.name = len(bugs)
        bug.node = node    # backlink
        bugs.add(bug)
        node.bug = bug
    return bugs

def step_bug(grid, bug):
    # emit heat.
    node = bug.node
    node.heat += HEAT
    if node.heat > TOLERANCE:
        # FFFUUUUUuuu!. Find a node to migrate to.
        neighbors = grid.neighbors(bug.node)
        for new_node in sorted(neighbors, key=attrgetter("heat")):
            if not new_node.bug:
                # yay, move
                new_node.bug = bug
                node.bug = None
                bug.node = new_node
                # cheat a little. TODO: give nodes __unicode__()
                LOG.debug("%s: %s -> %s" % (bug.name,
                    grid.inverted_node_map[node],
                    grid.inverted_node_map[new_node]))
                break

def diffuse(grid):
    """
    Rudimentary heat diffusion.
    """
    cardinality = len(grid.dimensions)
    heat_distribution_coeff = 2 ** cardinality
    heat_loss = 0.2
    for node in grid.cells():
        heat_gain = (node.heat * heat_loss) / heat_distribution_coeff
        for n in grid.neighbors(node):
            n.heat += heat_gain
        node.heat *= 1 - heat_loss

class BugNode(object):
    __slots__ = "bug", "heat"
    def __init__(self):
        self.heat = 0

def run_simulation(steps=50):
    g = GridSpace(cell_fn=BugNode)
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
