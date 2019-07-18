from typing import *

__all__ = ['Some', 'Non', 'Option']


class Option(object):
    def __bool__(self):
        return self.is_defined()

    @staticmethod
    def is_defined():
        raise NotImplementedError()

    @staticmethod
    def is_none():
        raise NotImplementedError()

    def get(self):
        raise NotImplementedError()

    def get_or(self, default):
        raise NotImplementedError()


class _Non(Option):
    @staticmethod
    def is_defined():
        return False

    @staticmethod
    def is_none():
        return True

    def map(self, f):
        return self

    def flatmap(self, f):
        return self

    @staticmethod
    def get():
        raise RuntimeError("Unwrapping a None")

    def get_or(self, default):
        return default

    def __str__(self):
        return 'None'

    def __repr__(self):
        return str(self)


Non = _Non()


class Some(Option):
    def __init__(self, val):
        self.val = val

    @staticmethod
    def is_defined():
        return True

    @staticmethod
    def is_none():
        return False

    def map(self, f):
        return Some(f(self.val))

    def flatmap(self, f):
        v = f(self.val)
        if not v or (isinstance(v, Option) and v.is_none()):
            return Non
        elif (isinstance(v, Option) and v.is_defined()):
            return v
        else:
            return Some(v)

    def get(self):
        return self.get_or(None)

    def get_or(self, default):
        return self.val

    def __str__(self):
        return "Some({})".format(self.val)

    def __repr__(self):
        return str(self)


################################## test ####################################
def test_option():
    x = Some(3)
    assert isinstance(x, Option)
    assert x.is_defined()
    assert not x.is_none()
    assert x.get() == 3
    assert x.get_or(4) == 3
    assert x.map(lambda x: x + 1).get() == 4
    assert x.map(lambda x: None).get() is None
    assert x.map(lambda x: Non).get().is_none()
    assert x.flatmap(lambda x: x + 1).get() == 4
    assert x.flatmap(lambda x: None).is_none()
    assert x.flatmap(lambda x: Non).is_none()
    assert x.flatmap(lambda x: Some(1)).get() == 1

    import pytest

    x = Non
    assert isinstance(x, Option)
    assert x is Non
    assert not x.is_defined()
    assert x.is_none()
    with pytest.raises(RuntimeError):
        x.get()
    assert x.get_or(4) == 4
    assert x.map(lambda x: x + 1).is_none()
    assert x.flatmap(lambda x: x + 1).is_none()
