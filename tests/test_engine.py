import unittest

from calculator.engine import CalcError, Engine, format_number


class BasicModeTest(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()

    def calc(self, expr):
        return format_number(self.engine.evaluate(expr))

    def test_arithmetic(self):
        self.assertEqual(self.calc("1+2×3"), "7")
        self.assertEqual(self.calc("(1+2)×3"), "9")
        self.assertEqual(self.calc("10÷4"), "2.5")
        self.assertEqual(self.calc("7−10"), "-3")

    def test_decimal(self):
        self.assertEqual(self.calc("0.1+0.2"), "0.3")

    def test_negate_and_percent(self):
        self.assertEqual(self.calc("−(5)"), "-5")
        self.assertEqual(self.calc("(50)÷100"), "0.5")

    def test_divide_by_zero(self):
        with self.assertRaises(CalcError):
            self.engine.evaluate("1÷0")

    def test_invalid(self):
        for bad in ["", "1+", "__import__('os')", "abc"]:
            with self.assertRaises(CalcError):
                self.engine.evaluate(bad)


if __name__ == "__main__":
    unittest.main()
