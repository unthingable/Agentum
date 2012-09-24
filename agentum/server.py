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
import gevent
from gevent.event import AsyncResult
from gevent.server import StreamServer
from gevent.pool import Group
from gevent.queue import Queue, Empty

from agentum.simulation import Simulation

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class WorkerCmd(Cmd):

    def __init__(self, worker, *args, **kwargs):
        Cmd.__init__(self, *args, **kwargs)
        self.worker = worker
        self.prompt = '%s> ' % worker.module.__name__

    def do_quit(self, s):
        return True

    def do_EOF(self, s):
        return True

    def do_step(self, s):
        self.worker.step()

    def do_run(self, s=100):
        self.worker.run(int(s))
