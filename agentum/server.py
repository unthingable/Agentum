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
import traceback

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
            traceback.print_exc()
            return True
    return wrapper


def _getone(obj, f):
    if isinstance(obj, dict):
        return obj[f]
    else:
        return getattr(obj, f)


def _setone(obj, f, v):
    prev = _getone(obj, f)
    # coerce types (should be part of model?)
    if prev:
        v = type(prev)(v)
    if isinstance(obj, dict):
        obj[f] = v
    else:
        setattr(obj, f, v)


def _hasattr(obj, field):
    if isinstance(field, list):
        fields = field
    else:
        fields = field.split('.')
    if len(fields) == 1:
        if isinstance(obj, dict):
            return field[0] in obj
        else:
            return hasattr(obj, fields[0])
    else:
        return _hasattr(_getone(obj, fields[0]), fields[1:])


def _setattr(obj, field, value):
    if isinstance(field, list):
        fields = field
    else:
        fields = field.split('.')
    if len(fields) == 1:
        _setone(obj, fields[0], value)
    else:
        _setattr(_getone(obj, fields[0]), fields[1:], value)


def _getattr(obj, field):
    if isinstance(field, list):
        fields = field
    else:
        fields = field.split('.')
    if len(fields) == 1:
        return _getone(obj, fields[0])
    else:
        return _getattr(_getone(obj, fields[0]), fields[1:])


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
        elif _hasattr(self.worker.sim, field):
            if value:
                _setattr(self.worker.sim, field, value)
                protocol.flush()
            else:
                attr = _getattr(self.worker.sim, field)
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
