import unittest
import acl


class T(unittest.TestCase):
    def test_known_roles(self):
        self.assertTrue(acl.allowed("editor"))
        self.assertFalse(acl.allowed("suspended"))
        self.assertFalse(acl.allowed("guest"))


if __name__ == "__main__":
    unittest.main()
