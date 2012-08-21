class Agent(object):

    def run(self, simulation):
        return True

class MetaAgent(object):
    '''
    An omnipresent agent, not needed to be treated as separate entities.

    A metaagent does not move nor keep its own state, instead it operates on
    the cells and their state.

    A metaagent only operates on the explicitly passed cell.

    Use it to represent nature: heat dissipation, grass, etc..
    '''

    # A default metaagent is present everywhere.
    def is_present_at(self, cell):
        return True

    #
    def run(self, simulation, cell):
        pass
