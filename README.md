Agentum
=======

Agent Based Modeling tookit

### Alpha warning!

This code is experimental as we are evaluating ways of making Agentum awesome. You _may_ have to update your models, check back frequently. Yes, we could put this in PyPi already, but then we'd break it and you'd be sad.

The best way to use Agentum at this point is probably by copying the provided examples.

# Goal

Create a better ABM toolkit.

## Freedom by minimalism

Agentum aims to not impose. It is built on the principle of not enforcing any specifics until necessary. You are free to use as little or as much of it as you need — the only restriction is following the conventions used by the piece you use (like Models and Fields). Everything else is open to implementation.

## Simplicity by modularity

By extension of the above, Agentum abstracts and separates visualization and control from the model engine as much as possible. There is a human-friendly protocol for transmitting data and receiving commands that works over both WebSockets and plain networks sockets — you can create your own client for your specific application or even use it directly. It should be easy enough to plug Agentum's data into many existing visualization frameworks.

Server side there is a simple declarative mechanism for wiring your data to the network machinery. See Models and Fields below.

## Scalability

Everything scales nowadays, and so will Agentum — soon. We are prototyping inter-agent communication and substrate sharding strategies.

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

Agentum is a simulation _server_ whose job is to execute the simulation and tell you how it went. It speaks a human friendly protocol to _clients_ and is even usable directly. Clients are the means of interacting with and visualizing the simulation.

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
    forest_fire>

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

That was fun, how do we make more?

# Writing simulations

The main ingredient of the simulation is the agent's `run()` function. At present we evaluate simulations in discrete steps, executing every agent's `run()` in sequence.

Agents, the space they occupy and the simulation itself keep state in various ways, at present there are no restrictions on how that is done. This will change in the future as Agentum grows to a distributed system.

## Simulation class

The Simulation class contains everything that is needed to run the simulation:

* state fields and substrate
* agents
* the setup() method

### setup()

Configures the simulation, called by the server. This is similar to `__init__()` in intent.

In setup() you initialize simulation parameters, create a substrate and populate the simulation with agents.

### Space

In many simulation agents need some form of space to exist in, while others are more modest (El Pharol, for example, only requires an integer counter to represent current bar attendance).

Currently we have `GridSpace`, a finite and discrete N-dimensional Cartesian space (grid of cells). Soon there will be `GraphSpace` (a graph of cells). At present the agents are rather nearsighted and can only inspect neighboring cells.

    simulation.space = GridSpace(CellClass, dimensions=(100, 100))

### Cells

Space is composed of cells which you define. A cell can be anything, but you usually want to subclass `Cell`, for example:

    class CellClass(Cell):
        my_parameter = 0

        def __init__(self, point):
            super(CellClass, self).__init__(self, point)
            self.agents = set() # agents currently in the cell

In a `GridSpace` cells are mapped to _points_ (implemented as simple coordinate tuples). Points can be used as cell addresses, and are also used downstream for visualization.

As there is a finite number of cells we have two ways of addressing them: by coordinate tuples or by ordinal numbers (after having numbered them).

## Agents and metaagents

An _agent_ is the operating unit in our simulations. Agents are entities capable of making decisions. An example would be a potential patron in El Pharol or a bug in the "heatbugs" model.

A _metaagent_ is a force of nature (or a singular entity) that is optionally omnipresent in the substrate. That is, a metaagent can exist in every cell or only in some, and we evaluate a metaagent on all cells at once. An example of a metaagent is a force that dissipates heat in the "heatbugs" model, after the bugs have finished their moves and emitted their heat portions into their immediate cells.

## Models and Fields

Models are the way to wire your simulation for remote control.

In its simplest form there are very little restrictions on agents and models, as long as they have the few known methods defined (like `run()` and `setup()`). The engine will run the simulation and deterministic life will quietly happen inside. Print statements will work as means of output.

With any luck, however, soon will come a time when you want to interact with the running simulation and visualize what is happening. Fortunately, communicating with a client is easy: have your agents subclass Model and create class variables as instances of Field (a pattern typically used in ORMs such as Django).

Agents, metaagents, cells and simulations themselves can be Models.

### Field types

To use Fields you must subclass Model. Using Fields accomplishes three things:

* we can describe the model to the client
* we can automatically communicate changes to Fields to the client (and the client would know what to do with that information because we told it what the fields are)
* the client can modify a Model's Field too.

Consequently, a Field defines method to:

* describe the Field, giving the client enough information to know how to display it (name, type, default value, etc.)
* externalize: what to tell the client when the value changes (i.e., translate a value)
* internalize: translate a value sent by the client

Currently we support several types and we will add more as we go alogn. Some are trivial and some are not.

#### `Integer` and `Float`

Just that.

#### `State`

A finite collection of named states (an enum).

#### `Field`

A generic field, no special treatment. Use it for anything.

#### `FuncField`

Handy if your attribute is a function. Serializes to the function name.

### Quantization and serialization

### Adding your own Fields

# Protocol

