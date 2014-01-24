from unittest import TestCase
from nose.tools import ok_, eq_
from .zitraders import Market, Order


def test_buy_limit():
    market = Market()
    market.buy(100)
    ok_(market.highest_buy)
    eq_(market.highest_buy.price, 100)
    eq_(market.highest_buy.quantity, 1)


def test_sell_limit():
    market = Market()
    market.sell(100)
    ok_(market.lowest_sell)
    eq_(market.lowest_sell.price, 100)
    eq_(market.lowest_sell.quantity, 1)


def test_unmet_limits():
    market = Market()
    market.buy(100, 5)
    market.sell(200, 10)
    # Should result in two unmet limit orders
    eq_(market.lowest_sell, Order(200, 10))
    eq_(market.highest_buy, Order(100, 5))


def test_buy_limit_sorting():
    market = Market()
    market.buy(100)
    market.buy(95)
    # make sure highest bid is still 100
    eq_(market.highest_buy, Order(100, 1))

    # now add a higher bid and check
    market.buy(105, 5)
    eq_(market.highest_buy, Order(105, 5))


def test_simple_trade():
    m = Market()
    m.sell(100)
    m.buy(150)

    ok_(not m.lowest_sell)
    ok_(not m.highest_buy)
    eq_(m.volume, 1)
    eq_(m.high, 100)
    eq_(m.low, 100)


def test_order_split():
    m = Market()
    m.sell(100)
    m.sell(120)
    m.buy(200, 5)

    # expect there to be 3 remaining limit orders
    eq_(m.highest_buy, Order(200, 3))
    eq_(m.lowest_sell, None)
    ok_(m.volume, 2)
    eq_(m.high, 120)
    eq_(m.low, 100)

    # test same with excess sell orders
    m.sell(130, 10)
    eq_(m.highest_buy, None)
    eq_(m.lowest_sell, Order(130, 7))
    eq_(m.volume, 5)
    eq_(m.high, 200)
    eq_(m.low, 100)


def test_reset():
    m = Market()
    m.sell(100, 2)
    m.buy(40, 12)
    m.sell(20, 3)
    m.reset()

    ok_(not m.lowest_sell)
    ok_(not m.highest_buy)
