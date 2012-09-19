"Serialization and protocol stuff"

"""
Protocol stuff.

Output:

sim <id>
sim in|out param [param [param] ...]
sim param value [param value [param value] ...]

sim space grid|graph
sim state run|stop|pause

step [num]

agent <id> in|out param [param [param] ...]
agent <id> param value [param value [param value] ...]

cell <id> in|out param [param [param] ...]
cell <id> param value [param value [param value] ...]

Input:

sim state run|stop|pause
sim step
agent|cell <id> param value
"""

import json
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Propagator(object):
    """
    A mixin that will inspect input/output/command fields and wire
    stuff up.
    """
    inputs = []
    outputs = []
    commands = []

    stream_name = 'set stream_name!'
    _id_seq = 0

    def id(self):
        self._id_seq += 1
        return self._id_seq

    def __setattr__(self, key, value):
        # May have to optimize this later
        if key in self.inputs or key in self.outputs:
            # tell the world the value has changed
            output = [self.stream_name, self.id(), key, json.dumps(value)]
            log.debug(' '.join(output))
        object.__setattr__(self, key, value)
