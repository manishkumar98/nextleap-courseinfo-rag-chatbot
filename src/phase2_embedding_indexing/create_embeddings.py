import os
import json

def create_vector_db(chunks_file, collection_name=None):
    """
    Simulated 'indexing' for the lightweight version.
    Since we use direct JSON search, we just verify the file exists.
    """
    if not os.path.exists(chunks_file):
        print(f"❌ Error: {chunks_file} not found.")
        return False

    print(f"✅ Fast-Sync: Verified {chunks_file} for lightweight keyword search.")
    return True

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    chunks_path = os.path.join(project_root, "data", "course_chunks.json")
    create_vector_db(chunks_path)
