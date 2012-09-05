"""
Simulation server
"""

"""
LIST
GET <sim id>    - return params
SET <sim id>
START <sim id>
STOP <sim id>
"""

class Server(object):

    clients = []
    simulations = []
    running_simulations = []

    def load_simulation(self, module):
        setup = getattr(module, 'setup', None)
        if not setup:
            raise Exception("No setup() found in module %s" % module.__name__)
        log.info("Loading simulation %s" % module.__name__)

        sim = Simulation()
        setup(sim)

        simulations.append(sim)

    def loop(self):
        """
        Start server loop
        """
        # accept zmq connections
