import json
import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_vector_db(chunks_file, collection_name="nextleap_knowledge_base"):
    """
    Loads text chunks and stores them in ChromaDB with embeddings.
    Uses OpenAI embeddings as specified in the architecture.
    """
    # 1. Load the chunks
    if not os.path.exists(chunks_file):
        print(f"❌ Error: {chunks_file} not found.")
        return

    with open(chunks_file, 'r') as f:
        chunks = json.load(f)

    # 2. Get API Key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("⚠️ Warning: OPENAI_API_KEY not found in .env.")
        print("Fallback: Using locally hosted embedding model (all-MiniLM-L6-v2) for now to proceed.")
        # Fallback to a local model if the key is missing
        embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    else:
        # Use OpenAI Embeddings as per architecture
        embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"
        )

    # 3. Setup ChromaDB client (persistent)
    persist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "vector_db")
    client = chromadb.PersistentClient(path=persist_dir)

    # 4. Create/Get collection (Delete existing to ensure fresh start)
    try:
        client.delete_collection(name=collection_name)
        print(f"🗑️ Deleted existing collection: {collection_name}")
    except:
        pass

    collection = client.create_collection(
        name=collection_name, 
        embedding_function=embedding_function
    )

    # 5. Prepare data for insertion
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    documents = [chunk['text'] for chunk in chunks]
    metadatas = [chunk['metadata'] for chunk in chunks]

    # 6. Add to collection
    print(f"🔄 Indexing {len(documents)} chunks into '{collection_name}'...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"✅ Success! Vector database created at: {persist_dir}")
    print(f"📍 Total chunks indexed: {collection.count()}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    chunks_path = os.path.join(project_root, "data", "course_chunks.json")
    
    create_vector_db(chunks_path)
