import unittest
import os
import sys
from dotenv import load_dotenv

# Path setup to import retriever
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phase3_retrieval.retriever import NextLeapRetriever

load_dotenv()

class TestPhase3Retrieval(unittest.TestCase):
    def setUp(self):
        self.retriever = NextLeapRetriever()

    def test_retrieval_integrity(self):
        """
        Verify that retrieval returns content with metadata (Source URLs).
        """
        query = "Show me the PM course details."
        results = self.retriever.retrieve(query, top_k=2)
        
        self.assertGreater(len(results), 0, "Retrieval should return at least 1 result")
        first_result = results[0]
        self.assertIn("content", first_result, "Result missing content field")
        self.assertIn("metadata", first_result, "Result missing metadata field")
        self.assertIn("source_url", first_result["metadata"], "Metadata missing source_url")
        self.assertTrue(first_result["metadata"]["source_url"].startswith("http"), "Invalid source URL")

if __name__ == "__main__":
    unittest.main()
