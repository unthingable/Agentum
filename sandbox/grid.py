from collections import namedtuple
Point = namedtuple("Point","x y")

class Cell(object):
    __slots__ = "heat"

    def __init__(self, heat=0):
        self.heat = heat

class Grid(object):
    def __init__(self, w=100, h=100):
        self.width = w
        self.height = h
        self.cells = dict((Point(x,y), Cell(0)) for x in range(w) for y in range(h))

    def __getitem__(self, xy):
        x,y = xy
        return self.cells[Point(x,y)]
