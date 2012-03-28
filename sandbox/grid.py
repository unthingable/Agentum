from itertools import product, izip, imap, ifilter
from abc import abstractmethod
from random import choice
import math

def memoize(f):
    cache = {}
    def decorated_function(*args):
        if args in cache:
            return cache[args]
        else:
            cache[args] = f(*args)
            return cache[args]
    return decorated_function

class Cell(object):
    __slots__ = "heat", "bug", "_init"

    def __init__(self, heat=0, bug=None):
        self.heat = heat
        self.bug = bug # only one bug allowed
        self._init = dict(heat=heat,bug=bug)

    def clear(self):
        self.heat = 0
        self.bug = None

    def reset(self):
        self.__init__(**self._init)

class CellSpace(object):
    """
    In a cellular (discrete) space agents can look around and move.
    """
    @abstractmethod
    def cells(self, traverse=None): pass

    @abstractmethod
    def neighbors(self, cell, r=1): pass

    @abstractmethod
    def distance(self, cell, r=1): pass

    @abstractmethod
    def clear(self): pass

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

    def __init__(self, dimensions=(100,100), names=None, cell_class=Cell):
        """
        dimensions: list of dimensions
        names:      optional list of dimension names
        cell_fn:    a function that returns a new cell instance

        Ex. (100,100,20) for a 3-dimensional 100x100x20 grid.
        """
        self._dimensions = dimensions
        self._dimension_names = names
        self.cell_class = cell_class
        # The grid is a dict keyed by coordinate tuple and valued by the Cell
        # object (for now).
        self.cell_map = dict((tuple(xyz), cell_class()) for xyz in product(*imap(xrange, dimensions)))
        self.inverted_cell_map = dict((v,k) for k,v in self.cell_map.iteritems())

    def clear(self):
        map(cell_class.clear, self.cells())
        # neighbors do not change, so neighbors() can stay memoized with a prefilled cache

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

    # without memoization this can be a little slow
    def _get_neighbor_indexes(self, cell, r=1):
        xyz = self.inverted_cell_map[cell]
        ranges = (xrange(x-r,x+r+1) for x in xyz)
        # wraparound modulo dimension
        ranges = (set(x%y for x in r) for r,y in izip(ranges, self.dimensions))
        # all the cells except center
        indexes = ifilter(lambda x: x != xyz, product(*ranges))
        return indexes

    @memoize
    def neighbors(self, cell, r=1):
        indexes = self._get_neighbor_indexes(cell, r)
        return imap(self.cell_map.get, indexes)

    def distance(self, cell1, cell2):
        a,b = [self.inverted_cell_map[x] for x in (a,b)]
        return math.sqrt(sum((ax - bx) ** 2 for ax,bx in izip(a,b)))

class GraphSpace(CellSpace):
    pass