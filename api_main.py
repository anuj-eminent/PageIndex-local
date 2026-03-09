from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio

from general_rag import generate_reply
from grpah import generate_reply_with_ollama
from page_index import PageIndex
import uvicorn  
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Parallel Inference API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the PageIndex class once to share its state across requests
page_index_instance = PageIndex()

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QueryRequest):
    question = request.question

    # generate_reply and generate_reply_with_ollama are synchronous, 
    # so we run them in a threadpool to not block the async event loop.
    task_general_rag = asyncio.to_thread(generate_reply, question)
    task_graph_ollama = asyncio.to_thread(generate_reply_with_ollama, question)
    
    # get_answer is an async method
    task_page_index = page_index_instance.get_answer(question)

    # Run all 3 tasks in parallel
    results = await asyncio.gather(
        task_general_rag, 
        task_graph_ollama, 
        task_page_index, 
        return_exceptions=True
    )

    def extract_result(res):
        if isinstance(res, Exception):
            return {"error": str(res)}
        return res

    return {
        "question": question,
        "results": {
            "general_rag": extract_result(results[0]),
            "grpah_ollama": extract_result(results[1]),
            "page_index": extract_result(results[2])
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
