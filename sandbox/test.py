import unittest

from grid import GridSpace, GraphSpace
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
        import networkx as nx
        graph = nx.geographical_threshold_graph(100,1.2)
        self.g = GraphSpace(graph)
        for idx, node in self.g.cells():
            self.g[idx] = sim.BugCell()
        self.bugs = sim.init_grid(self.g, numbugs=20)

    def testGraphStep(self):
        self.testSimStep()

    def testRunSim(self):
        sim.run_simulation(steps=1)

if __name__=="__main__":
    unittest.main()
