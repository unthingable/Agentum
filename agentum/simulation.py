'''
Simulation is agent's access to the simulated world.
'''

class Simulation(object):

    space = None    # A single "physical" space for now.
    networks = {}
    agents = []
    metaagents = []

    # Need a more elegant way of doing this...
    # Put your runtime stuff in here
    runtime = None

    @property
    def config():
        '''
        Return simulation config
        '''

# A smart container to propagate properties.
# Anything you want shared between agents goes here.
class Container(object):
    pass

# TODO: create a decorator to denote synchronized/exposed properties.
