import json
import os
import unittest
import chromadb
from dotenv import load_dotenv

load_dotenv()

class TestPhase2Embeddings(unittest.TestCase):
    def setUp(self):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.chunk_path = os.path.join(project_root, "data", "course_chunks.json")
        self.db_path = os.path.join(project_root, "data", "vector_db")

    def test_chunk_file_exists(self):
        self.assertTrue(os.path.exists(self.chunk_path), "course_chunks.json is missing")

    def test_vector_db_exists(self):
        self.assertTrue(os.path.exists(self.db_path), "vector_db folder is missing")

    def test_db_content(self):
        client = chromadb.PersistentClient(path=self.db_path)
        # Assuming the standard collection name from our architecture
        collection = client.get_collection(name="nextleap_knowledge_base")
        count = collection.count()
        self.assertGreater(count, 0, "No chunks found in the database")
        print(f"📊 Vector DB verified with {count} chunks.")

if __name__ == "__main__":
    unittest.main()
