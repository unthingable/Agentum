from agentum import protocol
from collections import defaultdict
import logging

from agentum import settings
from .field import Field

log = logging.getLogger(__name__)
log.setLevel(settings.LOGLEVEL)

# Stop interpreter "not defined" complaints
Model = None


class ModelMeta(type):
    def __new__(meta, class_name, bases, attrs):
        log.debug('%s: %s' % (class_name, attrs))
        # Look for fields
        fields = {}

        # Inherit parent fields
        for base in bases:
            if base == Model:
                base_fields = getattr(base, '_fields', None)
                if base_fields:
                    fields.update(base_fields)

        # Supplement our own
        for name, attr in attrs.iteritems():
            if isinstance(attr, Field):
                fields[name] = attr
                attrs[name] = attr.default
        attrs['_fields'] = fields
        # import ipdb; ipdb.set_trace()

        return super(ModelMeta, meta).__new__(meta, class_name, bases, attrs)


id_seq = defaultdict(int)
ids = {}


class Model(object):
    __metaclass__ = ModelMeta

    stream_name = 'set stream_name!'

    # def __init__(self):
    #     self.__keys__ = self.inputs + self.outputs

    def id(self):
        '''
        Sequential ID of the object.
        '''
        if not self in ids:
            id_seq[self.__class__] += 1
            ids[self] = id_seq[self.__class__]
        return str(ids[self])

    def __setattr__(self, key, value):
        # May have to optimize this later
        if protocol.active and (key in self._fields):
            field = self._fields[key]
            qvalue = field.quantize(value, getattr(self, key))
            # Tell the world the value has changed
            if qvalue:
                output = [self.stream_name, self.id(), key, value]
                # o = ' '.join(output)
                log.debug(output)
                protocol.send(output)
        object.__setattr__(self, key, value)

    def __fire__(self, keys=None):
        keys = keys or self._fields.keys()
        for key in keys:
            protocol.send([self.stream_name, self.id(), key,
                           getattr(self, key)])