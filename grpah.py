import ollama
import os
from dotenv import load_dotenv
from Knowledge_Graph.app.services.ans_question import AnswerQuestion

# Load environment variables from .env if present
load_dotenv()

def generate_reply_with_ollama(question: str, model_name: str = "gpt-oss:120b"):
    """
    Function to get context from Qdrant/Neo4j and generate a reply using an Ollama LLM.
    """
    print(f"Fetching context for the question: '{question}'...")
    
    # Initialize the AnswerQuestion class which connects to Qdrant & Neo4j
    qa_system = AnswerQuestion()
    
    # Get the context for the asked question
    try:
        context = qa_system.get_context_from_qdrant(question)
        context_text = "\n".join([str(c) for c in context]) if context else "No context found."
    except Exception as e:
        print(f"Error fetching context: {e}")
        context_text = ""
        context = []

    print(f"Context retrieved successfully.")
    
    prompt = (
        f"Use the following knowledge graph context to answer the user's question.\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )

    ollama_host = "https://ollama.com"
    ollama_api_key = os.getenv("OLLAMA_API_KEY", "")
    print(f"Connecting to Ollama at {ollama_host} using model '{model_name}'...")
    
    # Pass headers if an API Key is set for the Cloud connection
    headers = {}
    if ollama_api_key:
        headers["Authorization"] = f"Bearer {ollama_api_key}"
        
    client = ollama.Client(host=ollama_host, headers=headers)
    
    try:
        response = client.chat(model=model_name, messages=[
            {
                "role": "system", 
                "content": "You are a helpful assistant. Provide a clear and concise answer based only on the provided context. If the answer is not contained in the context, say that you don't know."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ])
        
        reply_content = response['message']['content']
        return {"context": context_text, "answer": reply_content}

    except Exception as e:
        return {"context": context_text, "answer": f"Error generating reply from Ollama: {str(e)}"}

if __name__ == "__main__":
    import sys
    
    # Allow reading a question from command line
    test_question = sys.argv[1] if len(sys.argv) > 1 else "What is the main topic?"
    
    reply = generate_reply_with_ollama(test_question)
    
    print("\n--- Ollama Based Reply ---")
    print(reply)
