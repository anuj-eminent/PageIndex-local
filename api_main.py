from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import asyncio
import os

from general_rag import generate_reply
from grpah import generate_reply_with_ollama
from page_index import PageIndex
from upload_file import insertion_data
import uvicorn  
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Parallel Inference API")

# Keep a single insertion_data instance to reuse across requests
insertion = insertion_data()

# Where uploaded PDFs will be stored (always overwritten)
SAMPLE_PDF_PATH = os.path.join(os.path.dirname(__file__), "sample.pdf")

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

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Validate extension
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save uploaded file (always overwrite)
    contents = await file.read()
    with open(SAMPLE_PDF_PATH, "wb") as f:
        f.write(contents)

    # Process the PDF using the existing pipeline
    try:
        insertion.enter_data_for_all(SAMPLE_PDF_PATH)
    except Exception as e:
        print(f"Processing failed: {e}")
        pass

    return {
        "success": True,
        "path": SAMPLE_PDF_PATH,
        "message": "File uploaded, saved as sample.pdf, and processed successfully."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
