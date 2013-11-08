#from random import random
'''
Why fields?

Because we want to:
* describe the field to the client, for vizualisation purposes
* provide custom quantization
'''

class Field(object):
    def __init__(self, default=None, quant=None, scale=None):
        '''
        quant: quantization amount (makes sense for numeric attributes)
        scale: scaling function (for tne moment, unused)
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

    def description(self):
        '''Return a self description (to send to the client)'''
        out = dict(name=self.__class__.__name__,
                   default=self.default,
                   quant=self.quant,
                   # scale=self.scale
                   )
        return out

    # Experimental
    def externalize(self, value):
        'Value as sent to client'
        return value

    def internalize(self, value):
        return self.from_string(value)


class State(Field):
    # Could also have been called "fixed set"
    def __init__(self, states=[], default=None, **kw):
        '''
        Allowable state descriptors:
        'string' or ('short id', 'string', {additional parameters})
        where short id and additional parameters are optional.
        '''
        if len(states) < 2:
            raise Exception('A state field must have more than '
                            'one possible state')
        self.states = states
        Field.__init__(self, default=default, **kw)

    def description(self):
        out = Field.description(self)
        out['states'] = self.states
        return out

    # This should probably be handled at the protocol level
    def quantize(self, value, original):
        if value == original:
            return None
        else:
            return value


class Range(Field):
    min_value = 0
    max_value = 100


class Integer(Field):
    default = 0
    from_string = int

    @classmethod
    def serialize(cls, value):
        return str(int(value))


class Float(Field):
    default = 0.0
    from_string = float


class UFloat(Float, Range):
    default = 0.0
    min_value = 0
    max_value = 1


class List(Field):
    default = []

    def __init__(self, field, *args, **kw):
        Field.__init__(self, *args, **kw)
        self.from_string = lambda x: map(field.from_string, x.split())


# need valideer?
class Dict(Field):
    default = {}


class SpaceField(Field):
    def externalize(self, value):
        return value.dimensions


class FuncField(Field):
    def externalize(self, value):
        return value.__name__
