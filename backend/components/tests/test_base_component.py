import unittest
from enum import Enum

from backend.components.base_component import BaseComponent


class TestBaseComponent(unittest.TestCase):

    def test_wrong_attributes(self):
        with self.assertRaises(TypeError):
            BaseComponent(None, 2, "3")

        with self.assertRaises(TypeError):
            BaseComponent(1, "s", "3")

        with self.assertRaises(TypeError):
            BaseComponent(1, 2, 5)

        with self.assertRaises(ValueError):
            BaseComponent(-6, 2, "3")

    def test_valid_attributes(self):
        BaseComponent(0, 2, "dupa")


if __name__ == "__main__":
    unittest.main()
