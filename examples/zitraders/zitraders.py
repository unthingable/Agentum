from collections import namedtuple
import operator
import random


from agentum.simulation import Simulation
from agentum.agent import Agent
# from agentum.model.field import Integer as I, Float as F, UFloat as UF
#from agentum.utils import adict


Order = namedtuple("Order", "price quantity")


class Market(object):

    def __init__(self):
        self.sell_orders = []
        self.buy_orders = []
        self.transactions = []
        self.reset()

    def reset(self):
        self.volume = 0
        self.high = 0
        self.low = float("inf")

        del self.sell_orders[:]
        del self.buy_orders[:]
        self.yesterdays_return = self.market_price
        del self.transactions[:]

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
        # print "transacting %s for %s" % (quant, price)
        self.transactions.append(Order(price, quant))
        self.volume += quant
        self.high = max(price, self.high)
        self.low = min(price, self.low)

    @property
    def lowest_sell(self):
        self.sell_orders.sort(key=operator.attrgetter("price"))
        return self.sell_orders[0] if self.sell_orders else None

    @property
    def highest_buy(self):
        self.buy_orders.sort(key=operator.attrgetter("price"))
        return self.buy_orders[-1] if self.buy_orders else None

    def print_market(self):
        print "H/L/V: %s %s %s" % (self.high, self.low, self.volume)

    @property
    def market_price(self):
        prices = sorted(x.price for x in self.transactions)
        even = (0 if len(prices) % 2 else 1) + 1
        half = (len(prices) - 1) / 2
        return sum(prices[half:half + even]) / float(even)

    @property
    def market_return(self):
        return abs(self.yesterdays_return - self.market_price)


class Trader(Agent):
    '''
    '''
    def trade(self, sim):
        price = random.randint(1, 100)
        quant = random.randint(1, 20)
        if random.random() > 0.5:
            sim.market.buy(price, quant)
        else:
            sim.market.sell(price, quant)


class ZIT(Simulation):
    """"
    Zero intellingence traders
    """
    market = Market()

    def sunset(self):
        # self.market.print_market()
        self.returns.append(self.market.market_return)
        self.prices.append(self.market.market_price)
        self.market.reset()

    def setup(self):
        self.returns = []
        self.prices = []
        self.agents = [Trader() for x in xrange(10)]
        self.steps = (Trader.trade, self.sunset)
