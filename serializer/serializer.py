class Serializable:
    def __init__(self):
        pass

    def serialize(self):
        raise NotImplemented()

    def deserialize(self, data):
        raise NotImplemented()

