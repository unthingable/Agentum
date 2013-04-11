Agentum
=======

Agent Based Modeling tookit

### Alpha warning!

This code is experimental as we are evaluating ways of making Agentum awesome. You _may_ have to update your models, check back frequently. Yes, we could put this in PyPi already, but then we'd break it and you'd be sad.

# Installing

You should already have the following:

* git
* Python 2.7
* virtualenv is optional, but recommended

1. ```git clone git://github.com/unthingable/Agentum.git```
1. ```cd Agentum```
1. ```mkvirtualenv agentum```
1. ```python setup.py develop```

If all goes well you should be able to do:

    $ agentum
    usage: agentum [-h] [-p] module

# Running Agentum

Running Agentum is simple: all you need is a path to a Python file containing the simulation class.

Agentum is a simulation _server_ whose job is to execute the simulation and tell you how it went. It speaks a human friendly protocol to _clients_ and is even usable directly.

## via web client

We provide a simple web client, this part is more experimental than most.

    $ agentum examples/heatbugs/heatbugs.py
    Connect to http://localhost:9990/

Then point your browser at http://localhost:9990/.

## via telnet

    $ agentum -p examples/forest_fire/forest_fire.py

In another window:

    $ telnet localhost 5000
    Trying 127.0.0.1...
    Connected to localhost.
    Escape character is '^]'.
    Welcome to simulation server
    ["agentum", {"protocol": "0.1.3"}]
    ["preamble", {"cell": {"point": {"1": [0, 0], "3": [0, 2], "2": [0, 1], "5": [1, 1], "4": [1, 0], "7": [2, 0], "6": [1, 2], "9": [2, 2], "8": [2, 1]}}, "models": {"ForestCell": {"state": {"default": "empty", "states": ["empty", "occupied", "burning"], "quant": null, "name": "State"}, "point": {"default": null, "quant": null, "name": "Field"}}, "ForestFire": {"dimensions": {"default": [3, 3], "quant": null, "name": "Field"}, "ignition": {"default": 0.3, "quant": null, "name": "Float"}, "fill": {"default": 0.5, "quant": null, "name": "Float"}}}, "sim": {"name": "forest_fire", "space": {"grid": [3, 3]}}}]

## Commands

The simulation server understands a handful of commands. In telnet mode you can enter them manually.

    forest_fire> help

    Documented commands (type help <topic>):
    ========================================
    render

    Undocumented commands:
    ======================
    EOF  help  quit  run  sim  step


#### step

Executes one step of the simulation.

    forest_fire> step
    ["frame", 1, {"cell": {"state": {"3": "occupied", "5": "occupied", "4": "occupied", "7": "occupied", "6": "occupied", "8": "occupied"}}}]
    forest_fire> step
    ["frame", 2, {"cell": {"state": {"1": "occupied", "2": "occupied"}}}]
    forest_fire> step
    ["frame", 3, {"cell": {"state": {"3": "burning", "5": "burning", "4": "burning", "7": "burning"}}}]

#### run N

Executes N steps. Output is given after the last executed step only.

    forest_fire> run 20
    ["frame", 23, {"cell": {"state": {"1": "empty", "3": "burning", "2": "burning", "5": "empty", "4": "occupied", "7": "burning", "6": "occupied", "9": "burning", "8": "empty"}}}]

### Querying

You can interact with simulation parameters

#### sim

Describe the makeup of the simulation. This only works with Fields (see below).

    forest_fire> sim
    {'fill': <agentum.model.field.Float object at 0x245c690>, 'dimensions': <agentum.model.field.Field object at 0x245c6d0>, 'ignition': <agentum.model.field.Float object at 0x245c650>}

Query a parameter:

    forest_fire> sim fill
    0.5
    forest_fire> sim ignition
    0.3

Parameters can also be set. Let's set ignition probability to 1...

    forest_fire> sim ignition 1
    {"sim": {"ignition": 1.0}}

... and watch it burn!

    forest_fire> step
    ["frame", 2, {"cell": {"state": {"1": "burning", "3": "burning", "2": "burning", "5": "burning", "4": "burning", "7": "burning", "9": "burning"}}}]

# Writing simulations

That was fun, how do we make more?

## Simulation class

The Simulation class contains everything that is needed to run the simulation:

* state fields and substrate
* agents
* the setup() method

### setup()

Configures the simulation, called by the server. This is similar to ```__init__()``` in intent.

In setup() you initialize simulation parameters, create a substrate and populate the simulation with agents.

### Space

In many simulation agents need some form of space to exist in, while others are more modest (El Pharol, for example, only requires an integer counter to represent current bar attendance).

Currently we have ```GridSpace```, which is a grid of cells. Soon there will be ```GraphSpace``` (a graph of cells).

    simulation.space = GridSpace(CellClass, dimensions=(100, 100))

### Cells

Space is composed of cells which you define. A cell can be anything, but you usually want to subclass `Cell`, for example:

    class CellClass(Cell):
        my_parameter = 0

        def __init__(self, point):
            super(CellClass, self).__init__(self, point)
            self.agents = set() # agents currently in the cell

In a `GridSpace` cells are assigned to _points_ (implemented as coordinate tuples). Points can be used as cell addresses.

## Agents and metaagents

## Models and fields

# Protocol
