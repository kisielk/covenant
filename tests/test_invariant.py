import unittest
from covenant.invariant import *
from covenant.exceptions import *

class InvariantTests(unittest.TestCase):
    def test_invariant(self):
        @invariant(lambda self: self.foo >= 0)
        class Foo(object):
            foo = 0

            def __init__(self):
                self.foo = 0

            def add(self, num):
                self.foo += num

        f = Foo()
        f.add(5)

        self.assertEqual(f.foo, 5)

        with self.assertRaises(InvariantViolationError):
            f.add(-6)


if __name__ == "__main__":
    unittest.main()
