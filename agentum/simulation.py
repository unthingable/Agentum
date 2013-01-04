'''
Simulation is agent's access to the simulated world.
'''
from .model import Model


class Simulation(Model):

    stream_name = 'sim'

    def __init__(self):
        self.space = None    # A single "physical" space for now.
        #networks = {}
        self.agents = []
        self.metaagents = []
