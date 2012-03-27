from itertools import product, izip, imap, ifilter
from abc import abstractmethod
from random import choice

class Cell(object):
    __slots__ = "heat", "bug"

    def __init__(self, heat=0, bug=None):
        self.heat = heat
        self.bug = bug # only one bug allowed

class CellSpace(object):
    """
    In a cellular (discreet) space agents can look around and move.
    """
    @abstractmethod
    def cells(self, traverse=None):
        # return cell iter
        pass

    @abstractmethod
    def get_neighbor_cells(self, cell, r=1):
        pass

    @staticmethod
    def tr_random(cells):
        """
        Random cell space traversal. All cells guaranteed to be visited once.
        """
        from collections import deque
        remaining = deque(cells)
        while remaining:
            remaining.rotate(choice(range(len(remaining))))
            yield remaining.pop()

class Grid(CellSpace):
    """
    CellSpace implemented as N-dimensional rectangular grid.
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
        self.cell_map = dict((tuple(xyz), cell_fn()) for xyz in product(*imap(xrange, dimensions)))
        self.inverted_cell_map = dict((v,k) for k,v in self.cell_map.iteritems())

    def __getitem__(self, xyz): return self.cell_map[xyz]

    def cells(self, traverse=None):
        if not traverse:
            return self.cell_map.itervalues()
        else:
            return traverse(self.cell_map.itervalues())

    @property
    def dimensions(self): return self._dimensions

    def __len__(self):
        return len(self.cell_map)

    def get_neighbor_cells(self, cell, r=1):
        xyz = self.inverted_cell_map[cell]
        ranges = (range(x-r,x+r+1) for x,y in izip(xyz, self.dimensions))
        # TODO: wraparound

        # all the cells except center
        indexes = ifilter(lambda x: x != xyz, product(*ranges))
        return imap(self.cell_map.get, indexes)

import math
def distance(a,b):
    return math.sqrt(sum((ax - bx) ** 2 for ax,bx in izip(a,b)))
