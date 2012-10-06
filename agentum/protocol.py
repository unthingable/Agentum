"Serialization and protocol stuff"

"""
Protocol stuff.

Output:

sim <id>
sim in|out param [param [param] ...]
sim param value [param value [param value] ...]

sim space grid|graph [grid_size]
sim state run|stop|pause

step [num]

agent|cell <id>|all in|out param [param [param] ...]
agent|cell <id>|all param value [param value [param value] ...]

Input:

sim state run|stop|pause
sim step
agent|cell <id> param value
"""

from collections import defaultdict
import json
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

queue = None
id_seq = defaultdict(int)
ids = {}

# questionable hack
active = True


def send(obj):
    if queue:
        if isinstance(obj, (str, unicode)):
            obj = obj.split()
        queue.put(json.dumps(obj))


class Propagator(object):
    """
    A mixin that will inspect input/output/command fields and wire
    stuff up.
    """
    inputs = []
    outputs = []
    commands = []

    stream_name = 'set stream_name!'

    def id(self):
        if not self in ids:
            id_seq[self.__class__] += 1
            ids[self] = id_seq[self.__class__]
        return str(ids[self])

    def __setattr__(self, key, value):
        # May have to optimize this later
        if active and (key in self.inputs or key in self.outputs):
            # tell the world the value has changed
            output = [self.stream_name, self.id(), key, value]
            # o = ' '.join(output)
            log.debug(output)
            send(output)
        object.__setattr__(self, key, value)

    def __fire__(self, keys=None):
        keys = keys or self.outputs + self.inputs
        for key in keys:
            send([self.stream_name, self.id(), key, getattr(self, key)])
