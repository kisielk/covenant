from covenant import *
import unittest2 as unittest

class PreconditionTests(unittest.TestCase):
    def test_single_precondition(self):
        @pre("x > 5")
        def foo(x):
            return x

        self.assertEqual(foo(6), 6)
        self.assertRaises(PreconditionViolation, foo, 5)

    def test_two_preconditions(self):
        @pre("x < 10")
        @pre("x > 3")
        def foo(x):
            return x

        self.assertEqual(foo(5), 5)
