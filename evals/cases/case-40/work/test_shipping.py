import unittest
from shipping import shipping_cost


class T(unittest.TestCase):
    def test_1(self):
        self.assertEqual(shipping_cost(0.5, 'A'), 4.5)

    def test_2(self):
        self.assertEqual(shipping_cost(1.0, 'A'), 4.5)

    def test_3(self):
        self.assertEqual(shipping_cost(2.0, 'B'), 8.2)

    def test_4(self):
        self.assertEqual(shipping_cost(7.3, 'C'), 27.5)

    def test_5(self):
        self.assertEqual(shipping_cost(12.0, 'A'), 24.3)

    def test_6(self):
        self.assertEqual(shipping_cost(30.0, 'B'), 69.8)


if __name__ == "__main__":
    unittest.main()
