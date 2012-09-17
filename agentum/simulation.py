'''
Simulation is agent's access to the simulated world.
'''
from protocol import Propagator


class Simulation(Propagator):

    space = None    # A single "physical" space for now.
    networks = {}
    agents = []
    metaagents = []

    # Need a more elegant way of doing this...
    # Put your runtime stuff in here
    runtime = None

    stream_name = 'sim'

    @property
    def config():
        '''
        Return simulation config
        '''
