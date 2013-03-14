'''
Simulation is agent's access to the simulated world.
'''
from .model import Model, field


class Simulation(Model):

    stream_name = 'sim'
#    space = field.SpaceField()

    def __init__(self):
        # self.space = None    # A single "physical" space for now.
        # networks = {}
        self.agents = []
        self.metaagents = []

    def id(self):
        return None
