from collections import deque
import random

from agentum.simulation import Simulation
from agentum.agent import Agent
from agentum.model import field


def coinflip(history):
    return random.choice((True, False))


class ElFarol(Simulation):
    total_people = 100
    history = deque()

    current_attendance = 0
    # This field gets tallied every night
    attendance = field.Integer()
    history_size = field.Integer(5)

    # It's closing time
    def after_step(self, stepnum):
        # update the Field to propagate attendance
        self.attendance = self.current_attendance
        self.history.append(self.attendance)
        while len(self.history) > self.history_size:
            self.history.popleft()
        # Close the bar
        self.current_attendance = 0

    # Here we try a new convention: putting setup() directly into
    # Simulation.
    def setup(self):
        # Write some history
        self.history = deque([30] * self.history_size)
        # Add some patrons with a strategy
        for x in xrange(self.total_people):
            self.agents.append(Patron(coinflip))


class Patron(Agent):
    strategy = field.FuncField()
    will_go = field.Field()

    def __init__(self, strategy):
        self.strategy = strategy

    def run(self, simulation):
        # Look at history and evaluate a strategy:
        self.will_go = self.strategy(simulation.history)
        if self.will_go:
            simulation.current_attendance += 1


simulation = ElFarol
