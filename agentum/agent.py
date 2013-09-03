from .model.model import Model  # hm


class Agent(Model):

    stream_name = 'agent'

    def run(self, simulation):
        return True
