import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NextLeapRetriever:
    def __init__(self, collection_name="nextleap_knowledge_base"):
        """
        Initializes the retriever by connecting to the persistent vector database.
        """
        # 1. Setup API keys and paths
        openai_api_key = os.getenv("OPENAI_API_KEY")
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        persist_dir = os.path.join(project_root, "data", "vector_db")

        # 2. Setup Embedding Function (matching Phase 2)
        if not openai_api_key:
            raise ValueError("❌ Error: OPENAI_API_KEY is required for production (to keep bundle size small). Please add it to your environment variables.")

        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"
        )

        # 3. Connect to ChromaDB
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_collection(
            name=collection_name, 
            embedding_function=self.embedding_function
        )

    def retrieve(self, query, top_k=4, threshold=1.2):
        """
        Performs a semantic search on the vector database.
        Returns a list of relevant text chunks and their source URLs.
        Filters out any chunks that exceed the similarity 'distance' threshold.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )

        formatted_results = []
        
        # Check if results are returned
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i]
                
                # Check against threshold (lower distance means higher similarity)
                if distance <= threshold:
                    formatted_results.append({
                        "content": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "score": distance
                    })
        
        return formatted_results

def format_context_for_llm(retrieved_chunks):
    """
    Helper to consolidate retrieved chunks into a single readable context block.
    """
    if not retrieved_chunks:
        return "No specific context found on nextleap.app."
    
    context_blocks = []
    sources = set()
    
    for i, chunk in enumerate(retrieved_chunks):
        context_blocks.append(f"[Fact {i+1}]: {chunk['content']}")
        sources.add(chunk['metadata'].get('source_url', 'www.nextleap.app'))
        
    return "\n".join(context_blocks), list(sources)

if __name__ == "__main__":
    # Test Retrieval with a sample query
    retriever = NextLeapRetriever()
    test_query = "What is the syllabus for PM course?"
    
    print(f"🔍 Searching knowledge base for: '{test_query}'...")
    relevant_chunks = retriever.retrieve(test_query, top_k=10)
    
    context, urls = format_context_for_llm(relevant_chunks)
    
    for i, chunk in enumerate(relevant_chunks):
        print(f"[{i+1}] Score: {chunk['score']:.4f} | Content: {chunk['content'][:100]}...")
    print("\n--- 🔗 Source URLs ---")
    print("\n".join(urls))
