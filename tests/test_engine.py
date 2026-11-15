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


class ScientificModeTest(unittest.TestCase):
    def setUp(self):
        self.engine = Engine(degrees=True)

    def calc(self, expr):
        return format_number(self.engine.evaluate(expr))

    def test_trig_degrees(self):
        self.assertEqual(self.calc("sin(30)"), "0.5")
        self.assertEqual(self.calc("cos(60)"), "0.5")
        self.assertEqual(self.calc("tan(45)"), "1")
        self.assertEqual(self.calc("sin(180)"), "0")
        self.assertEqual(self.calc("asin(1)"), "90")

    def test_trig_radians(self):
        self.engine.degrees = False
        self.assertEqual(self.calc("sin(π÷2)"), "1")
        self.assertEqual(self.calc("cos(pi)"), "-1")

    def test_tan_undefined(self):
        with self.assertRaises(CalcError):
            self.engine.evaluate("tan(90)")

    def test_power_and_root(self):
        self.assertEqual(self.calc("2^10"), "1024")
        self.assertEqual(self.calc("3^2"), "9")
        self.assertEqual(self.calc("√(16)"), "4")

    def test_log(self):
        self.assertEqual(self.calc("log(1000)"), "3")
        self.assertEqual(self.calc("ln(e)"), "1")
        self.assertEqual(self.calc("exp(0)"), "1")

    def test_factorial(self):
        self.assertEqual(self.calc("fact(5)"), "120")
        with self.assertRaises(CalcError):
            self.engine.evaluate("fact(2.5)")

    def test_domain_errors(self):
        for bad in ["√(−1)", "log(0)", "asin(2)", "2^100000", "unknown(1)"]:
            with self.assertRaises(CalcError):
                self.engine.evaluate(bad)


if __name__ == "__main__":
    unittest.main()
