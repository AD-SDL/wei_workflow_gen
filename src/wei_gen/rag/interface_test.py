import unittest
from .interface import RAG 

class TestRAG(unittest.TestCase):
    def setUp(self):
        # Setup the test environment
        self.workflow_rag = RAG()
        self.ot2_rag = RAG("ot2")

    def test_load_and_query_workflow(self):
        # Test if PCR workflows are retrieved from a super basic query
        results = self.workflow_rag.query("PCR Experiment", n_results=1)
        print("Query Results:", results)


    def test_load_and_query_ot2(self):
        # Test if ot2 configs are retrieved from a super basic query
        results = self.ot2_rag.query("PCR Experiment", n_results=1)
        print("Query Results:", results)

if __name__ == '__main__':
    unittest.main()
