from neo4j import GraphDatabase
import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
from Knowledge_Graph.app.services.retrival_graph import Neo4jReader
import ollama


load_dotenv()

class QudrantOperation():
    def __init__(self, collection_name="knowledge_base"):
        self.client = QdrantClient(url=os.getenv("QUADRANT_URL"), api_key=os.getenv("QUADRANT_API_KEY"))  
        self.collection_name = collection_name
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.model.get_sentence_embedding_dimension(),
                    distance=Distance.COSINE
                )
            )
        except Exception:
            pass

    def save_create_embedding(self, text: str):
        vector = self.model.encode(text).tolist()
        payload = {"text": text}
        point_id = str(uuid.uuid4())        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )
        return point_id
    
    def fetch_embedding(self, text: str):
        vector = self.model.encode(text).tolist()
        data = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            with_payload=True,
            limit=2
        )

        words = []
        for i in data.points:
            words.append(i.payload['text'])
        return words
    
class AnswerQuestion():
    def __init__(self):
        self.driver = GraphDatabase.driver((os.getenv("NEO4J_URI")), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")))
        self.qdrant_operation = QudrantOperation()
        self.graph = Neo4jReader()

    def fetch_relations(self):
        nodes = []
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN DISTINCT n.name AS name")
            for record in result:
                nodes.append(record["name"])
        return nodes
    
    def save_nodes_embedding(self):
        data = self.fetch_relations()
        for node in data:
            self.qdrant_operation.save_create_embedding(node)
        return "Done"
    
    def get_context_from_qdrant(self, text: str):
        words = self.qdrant_operation.fetch_embedding(text)
        context = []
        for word in words:
            context.append(self.graph.fetch_relations(word))
        return context
    
    def generate_reply(self, question: str, model: str = "qwen3.5:27b"):
        """
        Generates a reply to the asked question using Ollama and the context from Qdrant/Neo4j.
        """
        print(f"Fetching context for question: '{question}'...")
        context = self.get_context_from_qdrant(question)
        
        # Prepare context text
        context_text = "\n".join([str(c) for c in context])
        
        prompt = (
            f"Use the following knowledge graph context to answer the user's question.\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )

        try:
            print(f"Generating response using Ollama model '{model}'...")
            
            # Using the exact library host/params pattern if defined in .env, else defaults to local Ollama
            ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            client = ollama.Client(host=ollama_host)
            
            response = client.chat(model=model, messages=[
                {"role": "system", "content": "You are a helpful assistant. Provide a clear and concise answer based only on the provided context if possible."},
                {"role": "user", "content": prompt}
            ])
            
            return response['message']['content']
        except Exception as e:
            return f"Error generating reply: {str(e)}"
    


if __name__ == "__main__":
    question = "What is Malignant tumors"
    reply = AnswerQuestion().generate_reply(question)
    print("\n--- Generated Reply ---")
    print(reply)