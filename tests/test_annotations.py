import unittest
from covenant.annotations import *
from covenant.exceptions import *


class AnnotationTests(unittest.TestCase):
    def test_annotation(self):
        @constrain
        def foo(bar: lambda bar: bar > 10):
            pass

        foo(20)
        with self.assertRaises(PreconditionViolationError):
            foo(5)
