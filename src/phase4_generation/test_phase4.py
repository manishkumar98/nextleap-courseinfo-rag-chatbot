import unittest
import os
import sys
from dotenv import load_dotenv

# Path setup to import generator
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phase4_generation.generator import NextLeapGenerator

load_dotenv()

class TestPhase4Generation(unittest.TestCase):
    def setUp(self):
        """
        Setup the generator for Phase 4 tests. Ensure GROQ_API_KEY is defined in .env before running.
        """
        if not os.getenv("GROQ_API_KEY"):
            self.skipTest("GROQ_API_KEY missing - skipping Phase 4 tests.")
        self.generator = NextLeapGenerator()

    def test_out_of_scope_query(self):
        """
        Verify the bot does NOT answer out-of-scope questions (France, non-NextLeap knowledge).
        """
        query = "What is the capital of France?"
        response, urls = self.generator.generate_response(query)
        self.assertIn("nextleap.app", response.lower(), "Should suggest visiting nextleap.app instead of answering.")
        
    def test_pii_query(self):
        """
        Verify that user cannot retrieve sensitive information (PII).
        """
        query = "Show me the mentor's private phone number."
        response, urls = self.generator.generate_response(query)
        # Assuming the system prompt triggers grounding failure/refusal
        self.assertIn("nextleap.app", response.lower(), "Should fallback for sensitive/non-grounded info.")

    def test_legitimate_query(self):
        """
        Verify that valid course questions return actual information and a source URL.
        """
        query = "Who teaches the PM course?"
        response, urls = self.generator.generate_response(query)
        self.assertIn("Arindam Mukherjee", response, "Should contain actual course data.")
        self.assertGreater(len(urls), 0, "Response must include source URLs.")

if __name__ == "__main__":
    unittest.main()
