class adict(dict):
    def __init__(self, *args, **kwargs):
        super(adict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, attr):
        value = self.__dict__[attr]
        if isinstance(value, dict):
            return adict(value)
