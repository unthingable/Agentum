#from random import random


class Field(object):
    def __init__(self, default=None, quant=None, scale=None):
        '''
        quant: quantization amount (makes sense for numeric attributes)
        scale: scaling function (for tne moment unused)
        '''
        self.default = default
        self.quant = quant
        self.scale = scale  # todo: ponder

    def quantize(self, value, old_value=None):
        '''
        Return value quantized to the nearest step.
        If old_value is not none, return none if quantization
        step boundary has not been crossed.
        '''
        step = self.quant
        # Makes equal sense when step is None or 0
        if not step:
            return value

        q_new = round(value / step)

        if old_value is None:
            return q_new * step

        q_old = round(old_value / step)

        # Better to compare integers
        if q_new != q_old:
            return q_new * step
        else:
            return None


class State(Field):
    def __init__(self, default=None, states={}, **kw):
        if len(states) < 2:
            raise Exception('A state field must have more than '
                            'one possible state')
        self.states = states
        Field.__init__(self, default=default, **kw)


class Integer(Field):
    default = 0

    @classmethod
    def serialize(cls, value):
        return str(int(value))


class Float(Field):
    default = 0

    # def quantize(self, *args, **kw):
    #     if random() < 0.1:
    #         import ipdb; ipdb.set_trace()
    #     return Field.quantize(self, *args, **kw)
