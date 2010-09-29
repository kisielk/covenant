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

    def test_two_arguments(self):
        @pre("x % y == 0")
        @pre("x < 8")
        def foo(x, y):
            return x / y
        self.assertEqual(foo(4,2), 2)
        self.assertRaises(PreconditionViolation, foo, 4, 3)
        self.assertRaises(PreconditionViolation, foo, 10, 2)

    def test_three_preconditions(self):
        @pre("x > 0")
        @pre("x < 10")
        @pre("x % 2 == 0")
        def foo(x):
             return x
        self.assertEqual(foo(4), 4)

    def test_imports(self):
        def validate(x):
            return x > 5
        @pre("validate(x)", imports={"validate":validate})
        def foo(x):
            return x
        self.assertEqual(foo(6), 6)
        self.assertRaises(PreconditionViolation, foo, 5)
