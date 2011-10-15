import unittest
from covenant import *


class PreconditionTests(unittest.TestCase):
    def test_one_precondition(self):
        @pre("x > 5")
        def foo(x):
            return x
        self.assertEqual(foo.__name__, "foo")
        self.assertEqual(foo(6), 6)
        with self.assertRaises(PreconditionViolation):
            foo(5)

    def test_method(self):
        class Foo(object):
            @pre("x > 5")
            def foo(self, x):
                return x
        f = Foo()
        self.assertEqual(f.foo.__name__, "foo")
        self.assertEqual(f.foo(6), 6)
        with self.assertRaises(PreconditionViolation):
            f.foo(5)

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
        self.assertEqual(foo(4, 2), 2)
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

        @pre("validate(x)", imports={"validate": validate})
        def foo(x):
            return x

        self.assertEqual(foo(6), 6)
        with self.assertRaises(PreconditionViolation):
            foo(5)

    def test_args(self):
        @pre("len(args) > 1")
        def foo(*args):
            return len(args)
        self.assertEqual(foo(1, 2), 2)
        with self.assertRaises(PreconditionViolation):
            foo(1)

    def test_with_exception(self):
        @pre("float(x)")
        def foo(x):
            return x + 1.0
        self.assertAlmostEqual(foo(1.0), 2.0)
        with self.assertRaises(PreconditionViolation):
            foo("abcd")


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
            return a * 2
        self.assertEqual(foo(2), 4)

    def test_two_postconditions(self):
        @post("_c == a*2")
        @post("_c % 2 == 0")
        def foo(a):
            return a * 2

        self.assertEqual(foo(2), 4)

    def test_three_postconditions(self):
        @post("_c == a*2")
        @post("_c % 2 == 0")
        @post("True")
        def foo(a):
            return a * 2

        self.assertEqual(foo(2), 4)

    def test_with_exception(self):
        @post("float(_c)")
        def foo():
            return "abcd"
        with self.assertRaises(PostconditionViolation):
            foo()


class PostAndPreconditionTests(unittest.TestCase):
    def test_post_and_pre(self):
        @post("_c == a*2")
        @pre("a > 1")
        def foo(a):
            return a * 2

        self.assertEqual(foo(2), 4)
        with self.assertRaises(PreconditionViolation):
            foo(1)


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
