"""
.
"""
#import Tkinter
#import grid
from grid import CellSpace

class Agent(object):
    pass

HEAT = 1
TOLERANCE = 2

class Bug(Agent):
    __slots__ = "name", "cell"

#grid = new Grid()

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
        # ffuuuu
        # find a cell to migrate to
        neighbors = g.get_neighbor_cells(bug.cell)
        for new_cell in sorted(neighbors, key=lambda x: x.heat):
            if not new_cell.bug:
                # yay, move
                new_cell.bug = bug
                cell.bug = None
                bug.cell = new_cell
                break

def diffuse(grid):
    """
    Rudimentary heat diffusion.
    """
    cardinality = len(grid.dimensions)
    heat_distribution_coeff = 2 ** cardinality
    heat_loss = 0.2
    for cell in grid.cells():
        for n in grid.get_neighbor_cells(cell):
            n.heat += (cell.heat * heat_loss) / (heat_distribution_coeff)
        cell.heat *= heat_loss

class Diffuser(Agent):
    """
    Diffuse the heat.
    """
    pass

def draw(g):
    pass
