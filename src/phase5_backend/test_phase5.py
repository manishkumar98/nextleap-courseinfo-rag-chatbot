import os
import sys
import unittest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Path setup for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phase5_backend.main import app

load_dotenv()

class TestPhase5Backend(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """
        Verify the API root is accessible and healthy.
        """
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("online", response.json()["status"])

    def test_chat_valid_query(self):
        """
        Verify the chat endpoint returns a response for a valid NextLeap question.
        Note: Needs valid API keys in .env.
        """
        if not os.getenv("GROQ_API_KEY"):
            self.skipTest("GROQ_API_KEY missing - skipping chat API tests.")
            
        test_payload = {"query": "Who is the PM mentor?"}
        response = self.client.post("/chat", json=test_payload)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("answer", data)
        self.assertIn("sources", data)
        self.assertGreater(len(data["sources"]), 0, "Response must include citations.")

    def test_chat_out_of_scope(self):
        """
        Verify that out-of-scope queries (like the capital of France) trigger grounding logic.
        """
        if not os.getenv("GROQ_API_KEY"):
            self.skipTest("GROQ_API_KEY missing - skipping grounding test.")
            
        test_payload = {"query": "What is the capital of France?"}
        response = self.client.post("/chat", json=test_payload)
        
        self.assertEqual(response.status_code, 200)
        answer = response.json()["answer"].lower()
        self.assertIn("nextleap.app", answer, "Should suggest official NextLeap source or state missing info.")

if __name__ == "__main__":
    unittest.main()
