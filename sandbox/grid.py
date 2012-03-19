from itertools import product, izip

class Cell(object):
    __slots__ = "heat"

    def __init__(self, heat=0):
        self.heat = heat

class Grid(object):
    """
    N-dimensional rectangular grid.
    """

    def __init__(self, dimensions=(100,100), names=None, cell_fn=Cell):
        """
        dimensions: list of dimensions
        names:      optional list of dimension names
        cell_fn:    a function that returns a new cell instance

        Ex. (100,100,20) for a 3-dimensional 100x100x20 grid.
        """
        self._dimensions = dimensions
        self._dimension_names = names
        """
        The grid is a dict keyed by coordinate tuple and valued by the Cell
        object (for now).
        """
        self.cells = dict((tuple(xyz), cell_fn()) for xyz in product(*map(xrange, dimensions)))

    def __getitem__(self, xyz): return self.cells[xyz]

    @property
    def dimensions(self): return self._dimensions

import math
def distance(a,b):
    return math.sqrt(sum((ax - bx) ** 2 for ax,bx in izip(a,b)))
