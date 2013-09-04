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

# TDDO: move to git tag
VERSION = '0.2.0'

known_models = set()


def greet():
    send(['agentum', {'protocol': VERSION}], compress=False)
    # Announce models
    models = {}
    for model in known_models:
        models[model.__name__] = fdict = {}
        for name, field in model._fields.iteritems():
            fdict[name] = field.description()  # field.__class__.__name__
    send(['models', models])


# Push the object onto the client stream (websocket, etc.)
# Override to do meaningful stuff
def push(obj):
    print repr(obj)

# This is between us and downstream
_buffer_tree = {}

# questionable hack
active = True


def send(obj, compress=True):
    if push:
        if isinstance(obj, (str, unicode)):
            obj = obj.split()
        if compress:
            _buffer(obj)
        else:
            push(json.dumps(obj))


def flush(wrapper=None):
    out = dict(_buffer_tree)
    if wrapper:
        out = wrapper(out)
    if push:
        push(json.dumps(out))
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
