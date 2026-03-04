import os
import json
import re

class NextLeapRetriever:
    def __init__(self, data_file=None):
        """
        Ultra-lightweight keyword-based retriever.
        Zero dependencies (No Torch, No Transformers, No ChromaDB).
        """
        if data_file is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_file = os.path.join(project_root, "data", "course_chunks.json")
        
        self.chunks = []
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                self.chunks = json.load(f)
        
    def retrieve(self, query, top_k=5):
        """
        Simple BM25-style keyword matching.
        """
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return []

        scored_chunks = []
        for chunk in self.chunks:
            text = chunk['text'].lower()
            # Calculate match score (word overlap)
            matches = sum(1 for word in query_words if word in text)
            if matches > 0:
                # Boost if course abbreviation is in query
                course_id = chunk['metadata'].get('course', '').lower()
                if course_id and course_id in query_words:
                    matches += 5
                
                scored_chunks.append({
                    "content": chunk['text'],
                    "metadata": chunk['metadata'],
                    "score": matches
                })
        
        # Sort by best match
        scored_chunks.sort(key=lambda x: x['score'], reverse=True)
        return scored_chunks[:top_k]

def format_context_for_llm(retrieved_chunks):
    if not retrieved_chunks:
        return "Note: No specific document matches found. Answer based on general knowledge.", []
    
    context_blocks = []
    sources = set()
    for i, chunk in enumerate(retrieved_chunks):
        context_blocks.append(f"[Ref {i+1}]: {chunk['content']}")
        sources.add(chunk['metadata'].get('source_url', 'https://nextleap.app'))
        
    return "\n".join(context_blocks), list(sources)
