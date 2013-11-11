"""
Simulation server.

At this point the server is its own worker.
Once we come to the distributed phase we'll
separate the workers from the server.
"""

"""
LIST
LOAD (and reload if already loaded)
GET <sim id>    - return params
SET <sim id>
START <sim id>
STOP <sim id>
"""

"""
NOTE: gevent is slower (a lot!) when running on a VM:
http://stackoverflow.com/questions/10656953/redis-gevent-poor-performance-what-am-i-doing-wrong
"""

import logging
from cmd import Cmd
from functools import wraps

from agentum import protocol, settings

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(settings.LOGLEVEL)


def exit_on_exception(meth):
    @wraps(meth)
    def wrapper(*args, **kw):
        try:
            return meth(*args, **kw)
        except:
            return True
    return wrapper


class WorkerCmd(Cmd):

    def __init__(self, worker, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        self.worker = worker
        self.prompt = '%s> ' % worker.simclass.__name__

    @exit_on_exception
    def do_init(self, s):
        self.worker.sim_init(force=True)

    def do_quit(self, s):
        return True

    def do_EOF(self, s):
        pass
        # return True

    @exit_on_exception
    def do_step(self, s):
        self.worker.step()

    @exit_on_exception
    def do_run(self, s=100):
        self.worker.run(int(s))

    # Below: throw away and reengineer. Do not use as an example.

    # Parameter feedback prototype
    @exit_on_exception
    def do_sim(self, s):
        field, _, value = s.partition(' ')
        if not field:
            protocol.push(self.worker.sim._fields)
        elif hasattr(self.worker.sim, field):
            if value:
                setattr(self.worker.sim, field, value)
                protocol.flush()
            else:
                attr = getattr(self.worker.sim, field)
                if not hasattr(attr, '__call__'):
                    protocol.push(attr)
                else:
                    protocol.push(attr())

    # # Prototype cell interaction
    # def do_cell(self, s):
    #     field, _, value = s.partition(' ')
    #     if not field:
    #         # Hackity hack. This wil
    #         cell = self.worker.sim.space.cells()[0]
    #         protocol.push(cell._fields)

    # Frame render example (for demo only)
    def do_render(self, param):
        'Render one parameter of substrate'
