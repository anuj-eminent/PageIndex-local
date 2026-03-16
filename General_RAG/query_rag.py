import os
import ollama
from dotenv import load_dotenv
from General_RAG.insertion_data import QudrantOperation

load_dotenv()

class RAGQuery:
    def __init__(self, model_name=" "):
        # Initialize Qdrant operations from insertion_data
        self.qdrant_op = QudrantOperation()
        self.model = model_name
        
        # Setup Cloud-based Ollama API connection
        # It defaults to localhost if OLLAMA_HOST is not set in your .env file
        self.ollama_host = "https://ollama.com"
        self.client = ollama.Client(host=self.ollama_host,headers={"Authorization": os.getenv("OLLAMA_API_KEY")})
        
    def ask_question(self, question: str) -> str:
        """
        Fetch context using Qdrant and get reply from cloud-based Ollama API.
        """
        print(f"\n[1] Fetching context for: '{question}'...")
        # Get context from fetch_embedding based on the query
        context_chunks = self.qdrant_op.fetch_embedding(question)
        
        if not context_chunks:
            context_text = "No relevant context found."
        else:
            # Combine the returned list of chunks into a single context string
            context_text = "\n---\n".join(context_chunks)
            
        print("[2] Context retrieved successfully.")
        
        # Formulate prompt with context
        prompt = f"""Use the following context to answer the user's question. If you cannot answer it using the context, simply say that you don't know based on the provided information.

        Context:
        {context_text}

        Question: {question}

        Answer:"""

        print(f"[3] Sending request to Ollama API at {self.ollama_host} using model '{self.model}'...")
        try:
            # Send streaming or synchronous chat request to Ollama
            response = self.client.chat(model=self.model, messages=[
                {
                    "role": "system", 
                    "content": "You are a highly capable AI assistant that answers questions based ONLY on the provided context."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ])
            
            return {"context": context_text, "answer": response['message']['content']}
        except Exception as e:
            return {"context": context_text, "answer": f"\nError communicating with Ollama API: {str(e)}"}
