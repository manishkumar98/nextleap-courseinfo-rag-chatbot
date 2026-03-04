import os
import sys
from groq import Groq
from dotenv import load_dotenv

# Adding Phase 3 to path to import retriever
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from phase3_retrieval.retriever import NextLeapRetriever, format_context_for_llm

load_dotenv()

class NextLeapGenerator:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        """
        Initializes the Groq-based generator with strict grounding constraints.
        """
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ Error: GROQ_API_KEY not found in .env file.")
        
        self.client = Groq(api_key=api_key)
        self.model_name = model_name
        self.retriever = NextLeapRetriever()

    def generate_response(self, query, history=None):
        """
        Retrieves relevant context and generates a grounded response using Groq.
        Stripping external AI knowledge using strict threshold and forceful prompting.
        """
        # 1. Retrieve the 'facts' from our embeddings (using a stricter threshold of 1.1)
        retrieved_chunks = self.retriever.retrieve(query, top_k=8, threshold=1.1)
        
        # Grounding check: If no relevant info is found at all
        if not retrieved_chunks:
            return "I am sorry, but I do not have any information in my NextLeap knowledge base regarding that question. Please visit [nextleap.app](https://nextleap.app) for more details.", []

        # 2. Format the context and source URLs
        context, sources = format_context_for_llm(retrieved_chunks)

        # 3. Formulate the system prompt with EXTREME constraints
        system_prompt = f"""
        # IDENTITY & KNOWLEDGE CONSTRAINT
        You are a specialized NextLeap Knowledge Engine. 
        You have NO knowledge of the world, history, science, or general topics outside of what is provided below. 
        Forget everything you have been trained on except how to read and extract information from the [Context] provided.
        
        # STRICT GROUNDING RULES:
        1. ONLY answer using facts from the [Context] section below. 
        2. If the answer is not explicitly contained within the [Context], you MUST say: "I'm sorry, I don't have information on that. Please visit nextleap.app." do not try to guess.
        3. DO NOT use your internal pre-trained knowledge about NextLeap or any other entities.
        4. If the user query is about personal information (PII) or secrets, refuse immediately.
        5. DO NOT provide any information that is not cited in the [Context].
        
        # FORMATTING:
        - Be concise and factual.
        - Use bullet points and bold text for key details.
        
        [Context]:
        {context}
        """

        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add history if provided
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add current query
        messages.append({"role": "user", "content": query})

        # 4. Call Groq for high-speed inference
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=0.1, # Low temperature for factual consistency
            )
            answer = chat_completion.choices[0].message.content
            return answer, sources

        except Exception as e:
            return f"Error connecting to Groq: {str(e)}", []

    def generate_stream(self, query, history=None):
        """
        Retrieves context and yields tokens in real-time for SSE.
        """
        # 1. Retrieve context
        retrieved_chunks = self.retriever.retrieve(query, top_k=8, threshold=1.1)
        
        if not retrieved_chunks:
            yield "I am sorry, but I do not have any information in my NextLeap knowledge base regarding that question. Please visit [nextleap.app](https://nextleap.app) for more details.|||[]"
            return

        context, sources = format_context_for_llm(retrieved_chunks)

        # 2. Prompts
        system_prompt = f"""
        # IDENTITY & KNOWLEDGE CONSTRAINT
        You are a specialized NextLeap Knowledge Engine. 
        You have NO knowledge of the world, history, science, or general topics outside of what is provided below. 
        Forget everything you have been trained on except how to read and extract information from the [Context] provided.
        
        # STRICT GROUNDING RULES:
        1. ONLY answer using facts from the [Context] section below. 
        2. If the answer is not explicitly contained within the [Context], you MUST say: "I'm sorry, I don't have information on that. Please visit nextleap.app." do not try to guess.
        3. DO NOT use your internal pre-trained knowledge about NextLeap.
        4. If the user query is about personal information (PII) or secrets, refuse immediately.
        5. DO NOT provide any information that is not cited in the [Context].
        
        # FORMATTING:
        - Be concise and factual.
        - Use bullet points and bold text for key details.
        
        [Context]:
        {context}
        """

        messages = [{"role": "system", "content": system_prompt}]
        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": query})

        # 3. Stream from Groq
        try:
            stream = self.client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                temperature=0.1,
                stream=True,
            )
            
            # Yield tokens
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            # Finally yield sources (special separator)
            import json
            yield f"|||{json.dumps(sources)}"

        except Exception as e:
            yield f"Error connecting to Groq: {str(e)}|||[]"

if __name__ == "__main__":
    # Test the generator
    try:
        generator = NextLeapGenerator()
        
        test_queries = [
            "What is the cost of the PM Fellowship?",
            "Who are the instructors for the Data Analyst course?",
            "What is the capital of France?", # Should trigger grounding failure
            "Tell me the phone number of the instructor Arindam." # Should trigger privacy refusal
        ]

        for q in test_queries:
            print(f"\nUser: {q}")
            response, urls = generator.generate_response(q)
            print(f"AI: {response}")
            if urls:
                print(f"Sources: {', '.join(urls)}")
            print("-" * 30)
            
    except Exception as e:
        print(f"Failed to initialize generator: {e}")
