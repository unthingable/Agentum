from agentum import protocol
from collections import defaultdict
import logging

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

            # Fix this ugliness?
            if hasattr(field, 'from_string'):
                value = field.from_string(value)

            original = getattr(self, key)
            qvalue = field.quantize(value, original)
            # Tell the world the value has changed
            if qvalue:
                # Again, experimental:
                qvalue = field.externalize(qvalue)

                output = [self.stream_name, key, self.id(), qvalue]
                # o = ' '.join(output)
                log.debug('%r <- %r' % (qvalue, original))
                protocol.send(output)
        object.__setattr__(self, key, value)

    def __fire__(self, keys=None):
        keys = keys or self._fields.keys()
        for key in keys:
            protocol.send([self.stream_name, key, self.id(),
                           original])

