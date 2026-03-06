from neo4j import GraphDatabase
import os
import uuid
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from sentence_transformers import SentenceTransformer
import pdfplumber

load_dotenv()


class QudrantOperation():
    def __init__(self, collection_name="RAG_Database"):
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
    
    def create_chunks(self, pdf_path: str = "Brain Tumor MRI.pdf"): 
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                width = page.width
                height = page.height
                
                left_bbox = (0, 0, width / 2, height)
                right_bbox = (width / 2, 0, width, height)
                
                left_text = page.within_bbox(left_bbox).extract_text()
                right_text = page.within_bbox(right_bbox).extract_text()
                
                if left_text:
                    full_text += left_text + "\n"
                if right_text:
                    full_text += right_text + "\n"
                    
        chunk_size = 1000
        chunk_overlap = 200
        
        chunks = []
        start = 0
        while start < len(full_text):
            end = start + chunk_size
            chunk = full_text[start:end]
            chunks.append(chunk)
            start += chunk_size - chunk_overlap
            
        inserted_ids = []
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk:
                point_id = self.save_create_embedding(chunk)
                inserted_ids.append(point_id)
                
        return inserted_ids

if __name__ == "__main__":
    q = QudrantOperation()
    q.create_chunks()