import unittest
from .db import DB  # Replace 'your_module' with the name of your Python file containing the db class

class TestDBFunctionality(unittest.TestCase):
    def setUp(self):
        # Setup the test environment
        self.database = DB()

    def test_load_and_query(self):
        # Test if PCR workflows are retrieved from a super basic query
        results = self.database.query("PCR Experiment", n_results=1)
        print("Query Results:", results)

if __name__ == '__main__':
    unittest.main()
