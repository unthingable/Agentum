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
        self.sim = sim.Heatbugs()

    def testCellAdd(self):
        bug = self.sim.add_bug()
        self.assertTrue(bug is not None)

    def testCellOverAdd(self):
        bug = True
        index, cell = self.sim.grid.cells().next()
        for x in range(self.sim.properties.max_bugs_per_cell + 1):
            bug = self.sim.add_bug(index)
        self.assertTrue(bool(bug) == False)

    def testSimStep(self):
        return
        for bug in self.bugs:
            self.sim.step_bug(bug)

    def testGraph(self):
        return
        import networkx as nx
        graph = nx.geographical_threshold_graph(100,1.2)
        self.g = GraphSpace(graph)
        for idx, node in self.g.cells():
            self.g[idx] = sim.BugCell()
        self.bugs = sim.init_grid(self.g, numbugs=20)

    def testGraphStep(self):
        return
        self.testSimStep()

    def testRunSim(self):
        return
        sim.run_simulation(steps=1)

if __name__=="__main__":
    unittest.main()
