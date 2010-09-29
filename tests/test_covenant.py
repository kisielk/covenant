from covenant import *
import inspect
import unittest2 as unittest

class PreconditionTests(unittest.TestCase):
    def test_one_precondition(self):
        @pre("x > 5")
        def foo(x):
            return x
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo(6), 6)
        self.assertRaises(PreconditionViolation, foo, 5)

    def test_two_preconditions(self):
        @pre("x < 10")
        @pre("x > 3")
        def foo(x):
            return x
        self.assertEqual(foo.__name__, "foo") 
        self.assertEqual(foo(5), 5)
        self.assertRaises(PreconditionViolation, foo, 2)
        self.assertRaises(PreconditionViolation, foo, 11)
