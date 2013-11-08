from .model.model import Model  # hm
from .model.field import Field

class Agent(Model):

    stream_name = 'agent'
    sim = None

    point = Field()
