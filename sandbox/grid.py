from itertools import product, izip, imap, ifilter
from collections import namedtuple
from abc import abstractmethod, ABCMeta
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

class Node(object):
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

class NodeSpace(object):
    """
    Discrete space, to look around and travel through.
    Space is just a fabric onto which nodes are laid.

    Space's responsibility is:
    * arranging nodes in a structure
    * providing means of navigating this structure (r-neighborhoods)
    * providing spatial measurements (distance)

    Space is not responsible for knowing where agents are, where they are
    and what happens inside the nodes -- this is up to the simulation.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def nodes(self, traverse=None): pass

    @abstractmethod
    def neighbors(self, node, r=1): pass

#    @abstractmethod
#    def distance(self, node, r=1): pass

    @staticmethod
    def tr_random(nodes):
        """
        Random node space traversal. All nodes guaranteed to be visited once.
        """
        from collections import deque
        remaining = deque(nodes)
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

class GridSpace(NodeSpace):
    """
    CellSpace implemented as N-dimensional rectangular grid.
    """

    def __init__(self, dimensions=(100,100), names=None, node_fn=Node):
        """
        dimensions: list of dimensions
        names:      optional list of dimension names
        node_fn:    node creator function (or class)

        Ex. (100,100,20) for a 3-dimensional 100x100x20 grid.
        """
        self._dimensions = dimensions
        self._dimension_names = names
        # The grid is a dict keyed by coordinate tuple and valued by the node
        # object (for now).

        # Important to note: functions inside the tuple are evaluated for
        # _every_ tuple, not just once.
        self.node_map = dict((tuple(xyz), node_fn())
            for xyz in product(*imap(xrange, dimensions)))
        self.inverted_node_map = dict((v,k) for k,v in self.node_map.iteritems())

    def __getitem__(self, xyz): return self.node_map[xyz]

    def nodes(self, traverse=None):
        if not traverse:
            return self.node_map.itervalues()
        else:
            return traverse(self.node_map.itervalues())

    @property
    def dimensions(self): return self._dimensions

    def __len__(self):
        return len(self.node_map)

    # without memoization this can be a little slow
    def _get_neighbor_indexes(self, node, r=1):
        xyz = self.inverted_node_map[node]
        ranges = (xrange(x-r,x+r+1) for x in xyz)
        # wraparound modulo dimension
        ranges = (set(x%y for x in r) for r,y in izip(ranges, self.dimensions))
        # all the nodes except center
        indexes = ifilter(lambda x: x != xyz, product(*ranges))
        return indexes

    @memoize
    def neighbors(self, node, r=1):
        indexes = self._get_neighbor_indexes(node, r)
        return imap(self.node_map.get, indexes)

    def distance(self, node1, node2):
        a,b = [self.inverted_node_map[x] for x in (a,b)]
        return math.sqrt(sum((ax - bx) ** 2 for ax,bx in izip(a,b)))
