import sys
import unittest2 as unittest
from covenant import *
import inspect

class PreconditionTests(unittest.TestCase):
    def test_one_precondition(self):
        @pre("x > 5")
        def foo(x):
            return x
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo(6), 6)
        with self.assertRaises(PreconditionViolation):
            foo(5)

    def test_two_preconditions(self):
        @pre("x < 10")
        @pre("x > 3")
        def foo(x):
            return x
        self.assertEqual(foo.__name__, "foo") 
        self.assertEqual(foo(5), 5)
        with self.assertRaises(PreconditionViolation):
            foo(2)
        with self.assertRaises(PreconditionViolation):
            foo(11)

    def test_two_arguments(self):
        @pre("x % y == 0")
        @pre("x < 8")
        def foo(x, y):
            return x / y
        self.assertEqual(foo(4,2), 2)
        with self.assertRaises(PreconditionViolation):
            foo(4, 3)
        with self.assertRaises(PreconditionViolation):
            foo(10, 2)

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
        with self.assertRaises(PreconditionViolation):
            foo(5)

    def test_args(self):
        @pre("len(args) > 1")
        def foo(*args):
            return len(args)
        self.assertEqual(foo(1,2), 2)
        with self.assertRaises(PreconditionViolation):
            foo(1)

class PostconditionTest(unittest.TestCase):
    def test_one_postcondition(self):
        @post("_c == 5")
        def foo():
            return 5
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo(), 5)

    def test_failed_postcondition(self):
        @post("_c == 5")
        def foo():
            return 6
        with self.assertRaises(PostconditionViolation):
            foo()

    def test_with_arg(self):
        @post("_c == a*2")
        def foo(a):
            return a*2
        self.assertEqual(foo(2), 4)

    def test_two_postconditions(self):
        @post("_c == a*2")
        @post("_c % 2 == 0")
        def foo(a):
            return a*2
        self.assertEqual(foo(2), 4)

    def test_three_postconditions(self):
        @post("_c == a*2")
        @post("_c % 2 == 0")
        @post("True")
        def foo(a):
            return a*2
        self.assertEqual(foo(2), 4)

class PostAndPreconditionTests(unittest.TestCase):
    def test_post_and_pre(self):
        @post("_c == a*2")
        @pre("a > 1")
        def foo(a):
            return a*2
        self.assertEqual(foo(2), 4)
        with self.assertRaises(PreconditionViolation):
            foo(1)
