from agentum import protocol
from collections import defaultdict
import logging
import sys

from atom.catom import Member
from atom.api import AtomMeta, Atom

from agentum import settings
from .field import Field

log = logging.getLogger(__name__)
log.setLevel(settings.LOGLEVEL)


# Stop interpreter "not defined" complaints
class Model:
    pass


class ModelMeta(type):
    def __new__(meta, class_name, bases, attrs):
        log.debug('%s: %s' % (class_name, attrs))
        # Look for fields
        fields = {}

        # Inherit parent fields
        for base in bases:
            if issubclass(base, Model):
                base_fields = getattr(base, '_fields', None)
                if base_fields:
                    fields.update(base_fields)

        # Supplement our own
        for name, attr in attrs.iteritems():
            if isinstance(attr, Field):
                fields[name] = attr
                attrs[name] = attr.default
                log.debug('%s.%s > %s', class_name, name, attr.default)
        attrs['_fields'] = fields

        return super(ModelMeta, meta).__new__(meta, class_name, bases, attrs)

    def __call__(cls, *args, **kwds):
        # Register the model
        protocol.known_models.add(cls)
        return type.__call__(cls, *args, **kwds)

id_seq = defaultdict(int)
ids = {}


class Model(object):
    __metaclass__ = ModelMeta

    stream_name = 'set stream_name!'

    def __init__(self):
        self._fields_previous = {}

    def id(self):
        '''
        Sequential ID of the object.
        '''
        if not self in ids:
            id_seq[self.__class__] += 1
            ids[self] = id_seq[self.__class__]
        return self.stream_name[0] + str(ids[self])

    def __setattr__(self, key, value):
        # May have to optimize this later
        if protocol.active and (key in self._fields):
            field = self._fields[key]

            # Fix this ugliness?
            if hasattr(field, 'from_string'):
                value = field.from_string(value)

            original = getattr(self, key)
            if original != value:
                # maybe ignore completely?
                self._fields_previous[key] = original

            qvalue = field.quantize(value, original)
            # Tell the world the value has changed
            if qvalue is not None:
                # Again, experimental:
                qvalue = field.externalize(qvalue)

                output = filter(lambda x: x is not None,
                                (self.stream_name, key, self.id(), qvalue))
                # o = ' '.join(output)
                log.debug('%s: %r <- %r' % (key, qvalue, original))
                protocol.send(output)
        object.__setattr__(self, key, value)

    def __fire__(self, keys=None):
        keys = keys or self._fields.keys()
        for key in keys:
            protocol.send([self.stream_name, key, self.id(),
                           original])


def split_dict(d, test):
    a, b = {}, {}
    for k, v in d.iteritems():
        if test(k, v):
            a[k] = v
        else:
            b[k] = v
    return a, b


import inspect
class AtomizerMeta(type):
    def __new__(meta, class_name, bases, attrs):
        module = inspect.getmodule(inspect.stack()[1][0])
        if module.__name__ == meta.__module__ and class_name == 'Atomizer':
            # hide the magic until the real class comes along
            return super(AtomizerMeta, meta).__new__(meta, class_name, bases, attrs)

        # pluck out atom fields
        atom_attrs, basic_attrs = split_dict(attrs, lambda k,v: isinstance(v, Member))

        # remove Atomizer, will replace with two new classes
        new_bases = tuple(b for b in bases if b != Atomizer)
        new_classes = ()

        # allow use as both mixin and a sole superclass
        if not new_bases:
            basic_name = class_name + '_deatomized'
            basic_class = type(basic_name, new_bases, {})
            new_classes += ((basic_name, basic_class), )
            new_bases += (basic_class, )

        atom_name = class_name + '_atom'
        atom_class = type(atom_name, (Atom,), atom_attrs)
        new_classes += ((atom_name, atom_class), )
        new_bases += (atom_class, )

        # inject into the containg module
        for n, c in new_classes:
            setattr(module, n, c)
            setattr(c, '__module__', module.__name__)  # just in case

        return type(class_name, new_bases, basic_attrs)


class Atomizer(object):
    '''Smart atomizer'''
    __metaclass__ = AtomizerMeta


'''
Now we can do this!

from atom.api import Atom, Int
from agentum.model import model

class A(model.Atomizer):
    a = Int()
    b = 0
'''
