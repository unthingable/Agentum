'''
Simulation is agent's access to the simulated world.
'''

class Simulation(object):

    space = None    # A single "physical" space for now.
    networks = {}
    agents = []
    metaagents = []

    @property
    def config():
        '''
        Return simulation config
        '''


