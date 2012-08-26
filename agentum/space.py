'''
Space for agents to exist in
'''

from itertools import product, izip, imap, ifilter
from collections import namedtuple
from abc import abstractmethod, ABCMeta
from operator import itemgetter
from random import choice
from functools import wraps
import math

def memoize(f):
    """
    Warning: do not return iterators from memoized functions!
    """
    cache = {}
    @wraps(f)
    def decorated_function(*args, **kwargs):
        key = (args, tuple(kwargs.items()))
        if key in cache:
            return cache[key]
        else:
            return cache.setdefault(key, f(*args, **kwargs))
    return decorated_function

# how about: a cell is responsible for communicating its state changes
class Cell(object):
    """
    The basic element of our world. Must be hashable.
    """
    __slots__ = "properties", "agents"

    def __init__(self, properties=None):
        self.agents = set()
        self.properties = properties or {}


class SparseSpace(object):
    """
    N-dimensional cartesian space.
    Agents can inspect r-neighborhoods and move.
    """

class CellSpace(object):
    """
    Discrete space, to look around and travel through.
    Space is just a fabric onto which cells are laid.

    Space's responsibility is:
    * arranging nodes in a structure
    * providing means of navigating this structure (r-neighborhoods)
    * providing spatial measurements (distance)

    Space is not responsible for knowing where agents are, where they are
    and what happens inside the cells -- this is up to the simulation.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def cells(self, traverse=None): pass

    @abstractmethod
    def neighbors(self, cell, r=1): pass

    @abstractmethod
    def find(self, agent): pass

    @abstractmethod
    def move(self, agent, cell): pass

    @abstractmethod
    def add_agent(self, agent, cell): pass

    @abstractmethod
    def del_agent(self, agent): pass

    @abstractmethod
    def agents(self, with_cells=False): pass

#    @abstractmethod
#    def distance(self, node, r=1): pass

    @staticmethod
    def tr_random(items):
        """
        Full random node space traversal. All nodes guaranteed to be visited once.
        """
        from collections import deque
        remaining = deque(items)
        while remaining:
            remaining.rotate(choice(range(len(remaining))))
            yield remaining.pop()

#TODO: rename :)
def propertinator(properties):
    """
    Take a property bundle and return a slotted property class.
    A property bundle is either:
    * a list of property names
    * a list of tuples (property, defaulf value)
    * same as a dictionary
    * a mix thereor.

    Example: (("heat",0),"peace",{"love":"all you need"})
    """
    if not properties:
        return lambda: None
    property_names = []
    defaults = {}
    for p in properties:
        if not hasattr(p, "__iter__"):
            property_names.append(p)
        elif hasattr(p, "iteritems"):
            for k,v in p.iteritems():
                property_names.append(k)
            defaults.update(p)
        elif len(p) == 2:
            k,v = p
            property_names.append(k)
            defaults[k] = v
        else:
            raise Exception("Invalid property structure: %s" % repr(properties))

    class PropertyClass(object):
        __slots__ = tuple(property_names + ["_defaults"])
        _defaults = defaults

        def __init__(self):
            for k,v in self._defaults.iteritems():
                setattr(self,k,v)

    return PropertyClass

class GridSpace(CellSpace):
    """
    GridSpace implemented as N-dimensional rectangular grid.
    """

    def __init__(self, cell_fn, dimensions=(100,100), names=None):
        """
        dimensions: list of dimensions
        names:      optional list of dimension names
        cell_fn:    cell creator function (or class)

        Ex. (100,100,20) for a 3-dimensional 100x100x20 grid.
        """
        self._dimensions = dimensions
        self._dimension_names = names
        # The grid is a dict keyed by coordinate tuple and valued by the node
        # object (for now).

        # Important to note: functions inside the tuple are evaluated for
        # _every_ tuple, not just once.
        self.idx_cell_map = dict((tuple(xyz), cell_fn())
            for xyz in product(*imap(xrange, dimensions)))
        self.cell_idx_map = dict((v,k) for k,v in self.idx_cell_map.iteritems())

    # Expose coordinates
    def __getitem__(self, xyz): return self.idx_cell_map[xyz]

    def __setitem__(self, xyz, item):
        self.idx_cell_map[xyz] = item

    def cells(self, traverse=None):
        if not traverse:
            return self.idx_cell_map.values()
        else:
            return traverse(self.idx_cell_map.values())

    @property
    def dimensions(self): return self._dimensions

    def __len__(self):
        return len(self.idx_cell_map)

    # without memoization this can be a little slow
    def _get_neighbor_indexes(self, xyz, r=1):
        ranges = (xrange(x-r, x+r+1) for x in xyz)
        # wraparound modulo dimension
        ranges = (set(x%y for x in r) for r,y in izip(ranges, self.dimensions))
        # all the nodes except center
        indexes = ifilter(lambda x: x != xyz, product(*ranges))
        return indexes

    @memoize
    def neighbors(self, cell, r=1):
        index = self.cell_idx_map[cell]
        indexes = self._get_neighbor_indexes(index, r)
        return [self.idx_cell_map[idx] for idx in indexes]

    def distance(self, a, b):
        a,b = [self.cell_idx_map[x] for x in (a,b)]
        return math.sqrt(sum((ax - bx) ** 2 for ax,bx in izip(a,b)))

# TODO: same cell index semantic as CellSpace
# class GraphSpace(CellSpace):
#     def __init__(self, cell_fn, graph, cell_key="_cell"):
#         """
#         Create a GraphSpace from an existing graph.
#         """
#         self.cell_key = cell_key
#         self.graph = graph

#         if cell_fn:
#             for node, data in self.graph.nodes_iter(data=True):
#                 data[self.cell_key] = cell_fn()

#     def __getitem__(self, index): return self.graph.node[index][self.cell_key]

#     def __setitem__(self, index, item):
#         self.graph.node[index][self.cell_key] = item

#     def __len__(self):
#         return self.graph.size()

#     def cells(self, traverse=None):
#         for k,v in self.graph.nodes_iter(data=True):
#             yield k,v[self.cell_key]
#         #TODO: traverse function

#     @memoize
#     def neighbors(self, index, r=1):
#         if r == 1:
#             return tuple(self.graph.neighbors(index))
#         else:
#             raise Exception("Implement r-neighborhoods for GraphSpace first.")
