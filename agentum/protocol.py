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
Packed frame:
cell frame param [value, ...]

Input:

sim state run|stop|pause
sim step
agent|cell <id> param value
"""

from collections import defaultdict
import json
from operator import itemgetter

# This is downstream, let it do its own thing
queue = None

# This is between us and downstream
_buffer_tree = {}

# questionable hack
active = True


def send(obj, compress=True):
    if queue:
        if isinstance(obj, (str, unicode)):
            obj = obj.split()
        if compress:
            _buffer(obj)
        else:
            queue.put(json.dumps(obj))


def flush(wrapper=None):
    out = _buffer_tree
    if wrapper:
        out = wrapper(out)
    queue.put(json.dumps(out))
    _buffer_tree.clear()


def _buffer(obj, current_dict=_buffer_tree):
    '''
    Buffer a list/tuple object for subsequent compression.
    '''
    if len(obj) < 0:
        return
    if len(obj) == 1:
        # This should never happen, but if it does
        # we are prepared.
        current_dict[obj[0]] = None
    elif len(obj) == 2:
        current_dict[obj[0]] = obj[1]
    else:
        d = current_dict.setdefault(obj[0], {})
        _buffer(obj[1:], d)
