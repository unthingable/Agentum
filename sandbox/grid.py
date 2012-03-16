from itertools import product, izip

class Cell(object):
    __slots__ = "heat"

    def __init__(self, heat=0):
        self.heat = heat

class Grid(object):
    """
    N-dimensional rectangular grid.
    """

    def __init__(self, dimensions=(100,100)):
        """
        dimensions: list of dimensions.
        Ex. (100,100,20) for a 3-dimensional 100x100x20 grid.
        """
        self._dimensions = dimensions
        """
        The grid is a dict keyed by coordinate tuple and valued by the Cell
        object (for now).
        """
        self.cells = dict((tuple(xyz), Cell(0)) for xyz in product(*map(range, dimensions)))

    def __getitem__(self, xyz): return self.cells[xyz]

    @property
    def dimensions(self): return self._dimensions

import math
def distance(a,b):
    return math.sqrt(sum((ax - bx) ** 2 for ax,bx in izip(a,b)))
