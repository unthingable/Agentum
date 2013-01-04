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

queue = None

# questionable hack
active = True


def send(obj):
    if queue:
        if isinstance(obj, (str, unicode)):
            obj = obj.split()
        queue.put(json.dumps(obj))
