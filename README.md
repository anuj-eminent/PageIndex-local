# PageIndex Multi-Module RAG & Knowledge Graph System

A comprehensive Retrieval Augmented Generation (RAG) system combining three powerful modules: General RAG, Knowledge Graph with Neo4j, and PageIndex for intelligent document analysis and question-answering.

## Project Overview

This project integrates three distinct RAG/Knowledge systems:

1. **General_RAG**: Vector-based retrieval using Qdrant for semantic search
2. **Knowledge_Graph**: Graph-based retrieval using Neo4j and Qdrant with triple extraction
3. **PageIndex_Logic**: Hierarchical document indexing and retrieval system

All three modules work in parallel through a unified FastAPI interface.

## Project Structure

```
PageIndex-local/
├── api_main.py                 # Main FastAPI application (entry point)
├── general_rag.py              # General RAG wrapper
├── grpah.py                    # Knowledge Graph wrapper
├── page_index.py               # PageIndex wrapper
├── requirements.txt            # All project dependencies
├── .env                        # Environment configuration (see setup below)
│
├── General_RAG/                # General RAG Module
│   ├── query_rag.py           # RAG query interface
│   ├── insertion_data.py       # Data insertion to Qdrant
│   ├── Brain Tumor MRI.pdf     # Sample document
│   └── __pycache__/
│
├── Knowledge_Graph/            # Knowledge Graph Module
│   ├── requirements.txt        # Module dependencies
│   ├── app/
│   │   ├── main.py            # Knowledge Graph main app
│   │   └── services/
│   │       ├── ans_question.py        # Question answering logic
│   │       ├── chunking_documents.py  # Document chunking
│   │       ├── extracting_triplates.py # Triple extraction
│   │       ├── grpah_build.py         # Graph building
│   │       ├── neo4j_database.py      # Neo4j operations
│   │       ├── retrival_graph.py      # Graph retrieval
│   │       ├── text_extractor.py      # Text extraction
│   │       ├── triplets.txt
│   │       └── __pycache__/
│   └── Expriment PDF/
│
├── PageIndex_Logic/            # PageIndex Logic Module
│   ├── requirements.txt        # Module dependencies
│   ├── run_pageindex.py        # Main execution script
│   ├── query_structure.py      # Query interface
│   ├── list_ollama_models.py   # List available Ollama models
│   ├── test_concurrency.py     # Concurrency tests
│   ├── test_query_logic.py     # Unit tests
│   ├── pageindex/              # Core pageindex package
│   │   ├── __init__.py
│   │   ├── config.yaml         # Configuration file
│   │   ├── llm.py              # LLM integration
│   │   ├── page_index.py       # PageIndex implementation
│   │   ├── page_index_md.py    # Markdown support
│   │   ├── utils.py
│   │   └── __pycache__/
│   ├── cookbook/               # Example notebooks
│   │   ├── agentic_retrieval.ipynb
│   │   ├── pageIndex_chat_quickstart.ipynb
│   │   ├── pageindex_RAG_simple.ipynb
│   │   ├── vision_RAG_pageindex.ipynb
│   │   └── README.md
│   ├── results/                # Query results
│   ├── logs/                   # Execution logs
│   └── tutorials/              # Tutorial documentation
│
└── frontend/                   # Web UI (optional)
    ├── index.html
    ├── script.js
    └── styles.css
```

## Prerequisites

- Python 3.8 or higher
- Docker & Docker Compose (for containerized Neo4j and Qdrant)
- API Keys for:
  - OpenAI or OpenRouter (for LLM)
  - Qdrant Cloud or local Qdrant instance
  - Ollama API key (if using cloud Ollama)

## Installation & Setup

### 1. Clone/Setup Project

```bash
cd d:\Projects\PageIndex-local
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory (or update the existing one) with the following:

```env
# LLM Configuration
DEFAULT_MODEL=nvidia/nemotron-3-nano-30b-a3b:free
OPENROUTER_API_KEY=your_openrouter_api_key_here
OLLAMA_API_KEY=your_ollama_api_key_here

# Neo4j Configuration (Docker)
NEO4J_URI=neo4j://localhost:7687/
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password_here

# Qdrant Configuration (Cloud or Local)
QUADRANT_URL=https://your-instance.us-east-1-1.aws.cloud.qdrant.io:6333
QUADRANT_API_KEY=your_qdrant_api_key_here
```

### 5. Docker Setup (Recommended)

#### 5.1 Start Neo4j with Docker

```bash
# Pull Neo4j image
docker pull neo4j:latest

# Run Neo4j container
docker run -d \
  --name neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_secure_password_here \
  -e NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
  neo4j:latest

# Access Neo4j Browser at: http://localhost:7474
```

#### 5.2 Start Qdrant with Docker (Optional - if not using Cloud)

```bash
# Pull Qdrant image
docker pull qdrant/qdrant:latest

# Run Qdrant container
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Qdrant will be available at: http://localhost:6333
```

#### 5.3 Using Docker Compose (All-in-One)

Create a `docker-compose.yml` in the root directory:

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:latest
    container_name: neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/your_secure_password_here
      NEO4J_ACCEPT_LICENSE_AGREEMENT: "yes"
    volumes:
      - neo4j_data:/var/lib/neo4j/data

  qdrant:
    image: qdrant/qdrant:latest
    container_name: qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage

volumes:
  neo4j_data:
  qdrant_storage:
```

Run with Docker Compose:

```bash
docker-compose up -d
```

Stop services:

```bash
docker-compose down
```

### 6. Qdrant Cloud Setup

If using Qdrant Cloud (recommended for production):

1. Go to [Qdrant Cloud Console](https://cloud.qdrant.io)
2. Create a new cluster
3. Get your API endpoint and API key
4. Update `.env` file with:
   ```env
   QUADRANT_URL=https://your-cluster-url.cloud.qdrant.io:6333
   QUADRANT_API_KEY=your_api_key_here
   ```

### 7. Ollama Setup (Optional - for local LLM)

If you want to use Ollama locally instead of cloud:

```bash
# Download and install Ollama from https://ollama.ai
# Then pull a model:
ollama pull gpt-oss:120b

# Start Ollama server (runs on localhost:11434 by default)
ollama serve
```

To use local Ollama, update `.env`:

```env
OLLAMA_HOST=http://localhost:11434
```

## Execution Guide

### Main API Server (All-in-One)

Start the FastAPI server that runs all three modules in parallel:

```bash
# From root directory
python api_main.py

# Or using uvicorn directly
uvicorn api_main:app --reload --port 8000
```

The server will be available at: `http://localhost:8000`

**API Endpoint:**

```bash
# POST /ask - Query all three RAG systems
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is the main topic?\"}"
```

### General RAG Module Only

```bash
# Run from root directory
python -c "from general_rag import generate_reply; print(generate_reply('Your question here'))"

# Or execute the module directly
python General_RAG/insertion_data.py  # Insert documents
python General_RAG/query_rag.py        # Query documents
```

### Knowledge Graph Module

```bash
# From root directory - run the main app
python Knowledge_Graph/app/main.py

# Or test directly
python -c "from Knowledge_Graph.app.services.ans_question import AnswerQuestion; qa = AnswerQuestion(); print(qa.get_context_from_qdrant('Your question'))"
```

### PageIndex Module

```bash
# From root directory
python page_index.py

# Or run the main script
python PageIndex_Logic/run_pageindex.py

# List available Ollama models
python PageIndex_Logic/list_ollama_models.py

# Run tests
python PageIndex_Logic/test_query_logic.py
python PageIndex_Logic/test_concurrency.py
```

## Configuration Files

### Knowledge Graph Config

Edit `PageIndex_Logic/pageindex/config.yaml` for PageIndex-specific settings:

```yaml
# Model configuration
model: gpt-oss:120b
chunk_size: 512
overlap: 50

# Embedding model
embedding_model: sentence-transformers/all-MiniLM-L6-v2
```

### Example Query with Frontend

The frontend at `frontend/index.html` provides a web UI. Open it in your browser and query all three systems simultaneously.

## Troubleshooting

### Neo4j Connection Issues

```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check Neo4j logs
docker logs neo4j

# Restart Neo4j
docker restart neo4j
```

### Qdrant Connection Issues

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Test Qdrant API
curl http://localhost:6333/health

# Restart Qdrant
docker restart qdrant
```

### API Key Issues

- Ensure `.env` file is in the root directory
- Reload environment: `from dotenv import load_dotenv; load_dotenv()`
- Check API key validity with your service provider

### Module Import Errors

Ensure you run commands from the root directory (`d:\Projects\PageIndex-local`)

```bash
# Verify current directory
cd d:\Projects\PageIndex-local

# Install dependencies again
pip install -r requirements.txt
```

## Testing

Run the test files to validate each module:

```bash
# PageIndex concurrency tests
python PageIndex_Logic/test_concurrency.py

# PageIndex query logic tests
python PageIndex_Logic/test_query_logic.py
```

## API Documentation

Once the API server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Performance Notes

- The API runs all three RAG systems in parallel for maximum throughput
- Each system can be individually disabled by not calling its function
- Neo4j and Qdrant should be deployed on separate hardware for production
- Use connection pooling in production environments

## Contributing

When adding new features, ensure:

1. Dependencies are added to `requirements.txt`
2. Documentation is updated in this README
3. Environment variables are documented
4. Docker setup instructions are provided if needed

## Support

For issues related to:

- **Qdrant**: https://qdrant.tech/documentation/
- **Neo4j**: https://neo4j.com/docs/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Ollama**: https://ollama.ai/

## License

See LICENSE file for details.
