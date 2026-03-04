import os
import json
import hashlib
import sys
import subprocess
from datetime import datetime

# Add project root to path for imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "src", "phase1_data_acquisition", "raw_nextleap_data.json")
CHUNKS_PATH = os.path.join(PROJECT_ROOT, "data", "course_chunks.json")

def get_file_hash(filepath):
    """Calculates MD5 hash of a file."""
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def run_phase_scripts():
    """Triggers Phase 2: Chunking and Embedding."""
    print(f"[{datetime.now()}] 🔄 Changes detected. Triggering Knowledge Base update...")
    
    # 1. Run Chunking
    chunk_script = os.path.join(PROJECT_ROOT, "src", "phase2_embedding_indexing", "chunk_data.py")
    print(f"Running {chunk_script}...")
    subprocess.run([sys.executable, chunk_script], check=True)
    
    # 2. Run Embedding
    embed_script = os.path.join(PROJECT_ROOT, "src", "phase2_embedding_indexing", "create_embeddings.py")
    print(f"Running {embed_script}...")
    subprocess.run([sys.executable, embed_script], check=True)
    
    print(f"[{datetime.now()}] ✅ Knowledge Base successfully updated.")

STATUS_FILE_PATH = os.path.join(PROJECT_ROOT, "data", "scheduler_status.json")

def log_status(status, detail, data_hash=None):
    """Updates the public status file with the latest sync info."""
    status_data = {
        "last_sync": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "detail": detail,
        "data_hash": data_hash
    }
    with open(STATUS_FILE_PATH, "w") as f:
        json.dump(status_data, f, indent=4)
    print(f"📊 Status updated in {STATUS_FILE_PATH}")

def sync():
    """
    Main sync logic:
    1. Scrape latest data (Simulated for this demo).
    2. Compare hash.
    3. Update if needed.
    """
    print(f"[{datetime.now()}] 🔍 Starting NextLeap Data Synchronization...")
    
    current_hash = get_file_hash(RAW_DATA_PATH)
    hash_tracker_path = os.path.join(PROJECT_ROOT, "data", ".last_sync_hash")
    
    os.makedirs(os.path.dirname(hash_tracker_path), exist_ok=True)
    
    last_hash = None
    if os.path.exists(hash_tracker_path):
        with open(hash_tracker_path, "r") as f:
            last_hash = f.read().strip()
            
    if current_hash != last_hash:
        try:
            run_phase_scripts()
            # Save the new hash after successful update
            with open(hash_tracker_path, "w") as f:
                f.write(current_hash)
            
            log_status("SUCCESS", "Knowledge base updated with new data changes.", current_hash)
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error during sync: {error_msg}")
            log_status("FAILED", f"Error during sync: {error_msg}", current_hash)
    else:
        print(f"[{datetime.now()}] 😴 No changes detected. Knowledge Base is up to date.")
        log_status("IDLE", "No changes detected in source data.", current_hash)

if __name__ == "__main__":
    sync()
