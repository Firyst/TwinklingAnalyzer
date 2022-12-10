
import unittest
from LogicFunction import LogicFunction


class TestLogicFunction(unittest.TestCase):
    def setUp(self):
        self.func = LogicFunction('a + b + c')

    def test_vars(self):
        self.assertEqual(self.func.get_variables(), ['a', 'b', 'c'])

    def test_result(self):
        self.assertEqual(self.func.get_result((0, 1, 0)), 1)

    def test_table(self):
        self.assertEqual(self.func.generate_boolean_table(),
                         [((0, 0, 0), 0), ((0, 0, 1), 1), ((0, 1, 0), 1), ((0, 1, 1), 1), ((1, 0, 0), 1),
                          ((1, 0, 1), 1), ((1, 1, 0), 1), ((1, 1, 1), 1)])



# Executing the tests in the above test case class
if __name__ == "__main__":
    unittest.main()
