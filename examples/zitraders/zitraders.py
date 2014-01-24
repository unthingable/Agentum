from collections import namedtuple
import operator


from agentum.simulation import Simulation
from agentum.agent import Agent
from agentum.model.field import Integer as I, Float as F, UFloat as UF
#from agentum.utils import adict


Order = namedtuple("Order", "price quantity")


class Market(object):
    volume = 0
    high = 0
    low = float("inf")

    # limit orders
    sell_orders = []
    buy_orders = []

    # keep them nicely sorted

    def __init__(self):
        self.reset()

    def reset(self):
        self.volume = 0
        self.high = 0
        self.low = float("inf")

        del self.sell_orders[:]
        del self.buy_orders[:]

    def buy(self, price, quant=1):
        while quant and self.sell_orders and price >= self.lowest_sell.price:
            order = self.sell_orders.pop(0)
            # how much we can trade in a single iteration
            volume = min(quant, order.quantity)

            self.transact(order.price, volume)

            quant -= volume
            if volume < order.quantity:
                # Create a new limit order for the remaining amount
                # (effectively reducing the original order)
                self.sell_orders.append(Order(order.price,
                                              order.quantity - volume))
        if quant:
            # Create a limit order
            self.buy_orders.append(Order(price, quant))

    def sell(self, price, quant=1):
        while quant and self.buy_orders and price <= self.highest_buy.price:
            order = self.buy_orders.pop(-1)
            volume = min(quant, order.quantity)

            self.transact(order.price, volume)

            quant -= volume
            if volume < order.quantity:
                self.buy_orders.append(Order(order.price,
                                             order.quantity - volume))
        if quant:
            # Create a limit order
            self.sell_orders.append(Order(price, quant))

    def transact(self, price, quant):
        self.volume += quant
        self.high = max(price, self.high)
        self.low = min(price, self.low)

    @property
    def lowest_sell(self):
        self.sell_orders.sort(key=operator.itemgetter(0))
        return self.sell_orders[0] if self.sell_orders else None

    @property
    def highest_buy(self):
        self.buy_orders.sort(key=operator.itemgetter(0))
        return self.buy_orders[-1] if self.buy_orders else None


class Trader(Agent):
    '''
    '''
    # happiness = field.Float(1)
    color = None

    def trade(self, sim):
        pass


class ZIT(Simulation):
    '''
    Zero intellingence traders
    '''
    market = Market()

    def setup(self):
        pass
