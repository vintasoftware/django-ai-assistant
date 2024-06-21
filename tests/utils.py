class DictSubSet:
    def __init__(self, items: dict):
        self.items = items

    def __eq__(self, other):
        return self.items == {k: other[k] for k in self.items if k in other}

    def __repr__(self):
        return repr(self.items)
