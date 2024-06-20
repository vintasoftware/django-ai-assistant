from typing import Any


class DictSubSet:
    def __init__(self, items: dict):
        self.items = items

    def __eq__(self, other):
        return self.items == {k: other[k] for k in self.items if k in other}

    def __repr__(self):
        return repr(self.items)


def assert_ids(id1: Any, id2: Any, pk_setting: str):
    if pk_setting == "auto" or pk_setting == "string":
        assert id1 == id2
    elif pk_setting == "uuid":
        assert str(id1) == str(id2)
