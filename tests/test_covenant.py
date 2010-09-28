from covenant import *
import unittest2 as unittest

class PreconditionTests(unittest.TestCase):
    def test_simple(self):
        @pre(arg("x") > 5)
        def foo(x):
            return x

        self.assertEqual(foo(6), 6)
        self.assertRaises(PreconditionViolation, foo, 5)
