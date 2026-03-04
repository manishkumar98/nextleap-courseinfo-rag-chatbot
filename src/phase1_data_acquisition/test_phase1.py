import json
import os
import unittest

class TestPhase1Data(unittest.TestCase):
    def setUp(self):
        self.data_path = os.path.join(os.path.dirname(__file__), "raw_nextleap_data.json")
        self.md_path = os.path.join(os.path.dirname(__file__), "phase1_data.md")

    def test_json_file_exists(self):
        self.assertTrue(os.path.exists(self.data_path), "raw_nextleap_data.json is missing")

    def test_md_file_exists(self):
        self.assertTrue(os.path.exists(self.md_path), "phase1_data.md is missing")

    def test_data_integrity(self):
        with open(self.data_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn("courses", data)
        courses = data["courses"]
        self.assertEqual(len(courses), 5, "Should have data for 5 cohorts")
        
        for course in courses:
            self.assertTrue(course["title"], f"Missing title for {course}")
            self.assertTrue(course["url"], f"Missing url for {course['title']}")
            self.assertTrue(course["instructors"], f"No instructors found for {course['title']}")
            self.assertTrue(course["base_cost"], f"Missing cost for {course['title']}")

if __name__ == "__main__":
    unittest.main()
