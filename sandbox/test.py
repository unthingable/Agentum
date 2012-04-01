import unittest

from grid import GridSpace
import sim

class GridTest(unittest.TestCase):
    def setUp(self):
        class Cell(object):
            def __init__(self):
                self.heat = 0
        self.g = GridSpace((100,100), cell_fn=Cell)

    def testCreate(self):
        GridSpace()

    def testCreateWithProperties(self):
        self.assertEquals(self.g[0,0].heat, 0)

class SimTest(unittest.TestCase):
    def setUp(self):
        self.g = GridSpace(cell_fn=sim.BugCell)
        self.bugs = sim.init_grid(self.g, numbugs=20)

    def testSimStep(self):
        for bug in self.bugs:
            sim.step_bug(self.g, bug)

    def testGraph(self):
        return
        import networkx as nx
        self.g = nx.geographical_threshold_graph(100,1.2)
        for node in self.g.nodes_iter():
            self.g[node] = sim.BugCell()
        self.bugs = sim.init_grid(self.g, numbugs=20)

    def testGraphStep(self):
        return
        self.testSimStep()

    def testRunSim(self):
        sim.run_simulation(steps=1)

if __name__=="__main__":
    unittest.main()
