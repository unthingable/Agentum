import unittest

from grid import GridSpace
import sim

class GridTest(unittest.TestCase):
    def setUp(self):
        class Cell(object):
            def __init__(self):
                self.heat = 0
        self.g = GridSpace((100,100), node_fn=Cell)

    def testCreate(self):
        GridSpace()

    def testCreateWithProperties(self):
        self.assertEquals(self.g[0,0].heat, 0)

class SimTest(unittest.TestCase):
    def setUp(self):
        self.g = GridSpace(node_fn=sim.BugNode)
        self.bugs = sim.init_grid(self.g, numbugs=20)

    def testSimStep(self):
        for bug in self.bugs:
            sim.step_bug(self.g, bug)

if __name__=="__main__":
    unittest.main()
