import unittest
import os

class EmptyCsv(unittest.TestCase):
    def test_something(self):
        for file in os.listdir("data/csv"):
            n_lines = os.path.getsize("data/csv/" + file)
            self.assertTrue(n_lines > 0, msg=f"Csv file has {n_lines} lines")


if __name__ == '__main__':
    unittest.main()
