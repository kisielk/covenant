import unittest
from covenant.invariant import *


@unittest.skip("Not implemented yet")
class InvariantTests(unittest.TestCase):
    def test_invariant(self):
        self.skip()

        @invariant("self.foo >= 0")
        class Foo(object):
            def __init__(self):
                self.foo = 0

            def add(self, num):
                self.foo += num
        f = Foo()
        f.add(5)
        self.assertEqual(f.foo, 5)
        with self.assertRaises(InvariantViolation):
            f.add(-10)
        self.assertEqual(f.foo, 5)
        f.foo = -5
        with self.assertRaises(InvariantViolation):
            f.add(100)
        self.assertEqual(f.foo, -5)


if __name__ == "__main__":
    unittest.main()
