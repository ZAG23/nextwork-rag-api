# Nextwork RAG API

A Retrieval-Augmented Generation (RAG) API built with FastAPI, ChromaDB, and Ollama. This API allows you to add documents to a knowledge base and query them using AI-powered responses.

## Features

- **Add Knowledge**: Dynamically add text content to the knowledge base
- **Query Knowledge**: Ask questions and get AI-generated answers based on the stored knowledge
- **Persistent Storage**: Uses ChromaDB for persistent vector storage
- **AI Integration**: Uses Ollama for generating contextual answers

## Prerequisites

- **Python 3.11, 3.12, or 3.13** (Python 3.14 has compatibility issues with ChromaDB)
- [Ollama](https://ollama.ai/) installed and running
- The `tinyllama` model installed in Ollama (or modify the model name in `app.py`)

> **Note:** Python 3.14 is not yet supported by ChromaDB. Use Python 3.13 or earlier for best compatibility.

### Installing Ollama and the Model

1. Install Ollama from [https://ollama.ai/](https://ollama.ai/)
2. Pull the tinyllama model:
   ```bash
   ollama pull tinyllama
   ```

## Setup

1. **Clone the repository** (if applicable) or navigate to the project directory

2. **Create a virtual environment** (using Python 3.13):
   ```bash
   python3.13 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Embed initial documents** (optional):
   ```bash
   python embed.py k8s.txt
   ```
   Or embed any text file:
   ```bash
   python embed.py your_file.txt
   ```

## Running the API

### Option 1: Local Development

Start the FastAPI server:

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

### Option 2: Docker (Recommended)

#### Using Pre-built Image from Docker Hub

The image is available on Docker Hub as `zag23/rag-app:latest`:

```bash
# Pull the image
docker pull zag23/rag-app:latest

# Run the container
docker run -d -p 8000:8000 --name rag-app zag23/rag-app
```

**Important Notes for Docker:**
- The container expects Ollama to be running on the host machine
- On **Mac/Windows**: The container will automatically connect to `host.docker.internal:11434`
- On **Linux**: You may need to set `OLLAMA_HOST` to your host's IP address:
  ```bash
  docker run -d -p 8000:8000 -e OLLAMA_HOST=host.docker.internal:11434 --name rag-app zag23/rag-app
  ```
  Or use `--network host`:
  ```bash
  docker run -d --network host --name rag-app zag23/rag-app
  ```

#### Building from Source

To build the Docker image locally:

```bash
docker build -t zag23/rag-app .
docker run -d -p 8000:8000 --name rag-app zag23/rag-app
```

### API Documentation

Once the server is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## API Endpoints

### `GET /`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "Nextwork RAG API is running"
}
```

### `POST /add`
Add new content to the knowledge base.

**Request Body:**
```json
{
  "text": "Your content here..."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Content added to knowledge base",
  "id": "uuid-here"
}
```

### `POST /query`
Query the knowledge base and get an AI-generated answer.

**Request Body:**
```json
{
  "q": "What is Kubernetes?",
  "n_results": 1,
  "include_scores": false,
  "use_best_only": true
}
```

**Parameters:**
- `q` (required): The question to search for
- `n_results` (optional, default: 1): Number of results to retrieve (1-10)
- `include_scores` (optional, default: false): Include relevance scores in response
- `use_best_only` (optional, default: true): If true, only use best result for AI answer; if false, combine all results

**Response (basic):**
```json
{
  "answer": "Kubernetes is a container orchestration platform...",
  "results_count": 1
}
```

**Response (with scores and multiple results):**
```json
{
  "answer": "Kubernetes is a container orchestration platform...",
  "results_count": 3,
  "results": [
    {
      "id": "doc-id-1",
      "text": "Kubernetes is a container orchestration...",
      "relevance_score": 0.9234,
      "distance": 0.0832
    },
    {
      "id": "doc-id-2",
      "text": "Kubernetes helps manage containers...",
      "relevance_score": 0.8567,
      "distance": 0.1673
    }
  ]
}
```

### `DELETE /delete/{doc_id}`
Delete a document from the knowledge base by its ID.

**Path Parameters:**
- `doc_id`: The unique ID of the document to delete (returned when adding a document)

**Response:**
```json
{
  "status": "success",
  "message": "Document 'uuid-here' deleted successfully",
  "id": "uuid-here"
}
```

**Error Responses:**
- `404`: Document not found
- `400`: Invalid document ID

## Usage Examples

### Using cURL

**Add content:**
```bash
curl -X POST "http://localhost:8000/add" \
  -H "Content-Type: application/json" \
  -d '{"text": "FastAPI is a modern web framework for building APIs with Python."}'
```

**Query (basic):**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"q": "What is FastAPI?"}'
```

**Query (with multiple results and scores):**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "q": "What is FastAPI?",
    "n_results": 3,
    "include_scores": true,
    "use_best_only": false
  }'
```

**Delete document:**
```bash
curl -X DELETE "http://localhost:8000/delete/your-document-id-here"
```

### Using Python

```python
import requests

# Add content
response = requests.post(
    "http://localhost:8000/add",
    json={"text": "Your content here"}
)
print(response.json())

# Query (basic)
response = requests.post(
    "http://localhost:8000/query",
    json={"q": "Your question here"}
)
print(response.json()["answer"])

# Query (with multiple results and scores)
response = requests.post(
    "http://localhost:8000/query",
    json={
        "q": "Your question here",
        "n_results": 3,
        "include_scores": True,
        "use_best_only": False
    }
)
data = response.json()
print(f"Answer: {data['answer']}")
print(f"Found {data['results_count']} results")
for i, result in enumerate(data.get('results', []), 1):
    print(f"  Result {i} (score: {result.get('relevance_score', 'N/A')}): {result['text'][:100]}...")

# Delete document
doc_id = "your-document-id-here"
response = requests.delete(f"http://localhost:8000/delete/{doc_id}")
print(response.json())
```

## Project Structure

```
nextwork-rag-api/
├── app.py              # FastAPI application with RAG endpoints
├── embed.py            # Script to embed documents into ChromaDB
├── Dockerfile          # Docker configuration for containerized deployment
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── test_connection.py  # Test script to verify Ollama and ChromaDB connections
├── .gitignore         # Git ignore rules
├── db/                # ChromaDB database files (auto-generated)
└── k8s.txt           # Example text file for embedding
```

## Configuration

All configuration is done via environment variables. No code changes needed!

### Environment Variables

- `OLLAMA_HOST`: Ollama server address in `hostname:port` format (e.g., `localhost:11434` or `host.docker.internal:11434`)
  - Default: `localhost:11434`
  - **Note**: The Ollama Python client expects `hostname:port` format, not a full URL. Protocol prefixes are automatically removed.

- `OLLAMA_MODEL`: The Ollama model to use for generating answers
  - Default: `tinyllama`
  - Example: `export OLLAMA_MODEL=llama2` (after running `ollama pull llama2`)

- `CHROMA_DB_PATH`: Path where ChromaDB stores its database files
  - Default: `./db`
  - Example: `export CHROMA_DB_PATH=/data/rag-db`

- `CHROMA_COLLECTION_NAME`: Name of the ChromaDB collection to use
  - Default: `docs`
  - Example: `export CHROMA_COLLECTION_NAME=knowledge_base`

### Example Configuration

```bash
# Set all environment variables
export OLLAMA_HOST=localhost:11434
export OLLAMA_MODEL=llama2
export CHROMA_DB_PATH=./db
export CHROMA_COLLECTION_NAME=docs

# Then start the server
uvicorn app:app --reload
```

## Troubleshooting

1. **Ollama connection error**: 
   - Make sure Ollama is running (`ollama serve`)
   - For Docker: Ensure Ollama is accessible from the container (use `host.docker.internal:11434` on Mac/Windows)
   - Check that `OLLAMA_HOST` is set correctly (should be `hostname:port` format, not a URL)

2. **Model not found**: Ensure the model is installed (`ollama pull tinyllama`)

3. **Empty query results**: Make sure you've added content to the knowledge base first using `/add` endpoint or `embed.py`

4. **Port already in use**: Change the port with `uvicorn app:app --port 8001` or use a different port in Docker: `docker run -p 8001:8000 ...`

5. **Docker container can't connect to Ollama**:
   - Verify Ollama is running on the host: `curl http://localhost:11434/api/tags`
   - On Linux, you may need to use `--network host` or set `OLLAMA_HOST` to your host's IP
   - Check container logs: `docker logs rag-app`

6. **Test connections**: Use the provided test script:
   ```bash
   python test_connection.py
   ```

## Recent Updates

### Latest Changes

- **Query improvements**: 
  - Support for multiple results (configurable `n_results`, max 10)
  - Relevance scores and distance metrics
  - Option to combine all results or use only the best match
  - Enhanced response format with detailed result metadata
- **Environment variable configuration**: All settings (model, DB path, collection name) now configurable via environment variables - no code changes needed!
- **Improved error messages**: More actionable error messages that help users diagnose issues (connection problems, missing models, empty knowledge base, etc.)
- **DELETE endpoint**: Added `/delete/{doc_id}` endpoint to remove documents from the knowledge base
- **Fixed Ollama client response handling**: Changed from dictionary access (`answer["response"]`) to attribute access (`answer.response`) to match the Ollama Python client API
- **Improved Ollama host configuration**: Added automatic protocol stripping for `OLLAMA_HOST` environment variable to handle both URL and hostname:port formats
- **Docker support**: Added Dockerfile and published image to Docker Hub (`zag23/rag-app:latest`)
- **Connection testing**: Added `test_connection.py` script to verify Ollama and ChromaDB connections

### Docker Hub

The working image is available on Docker Hub:
- **Repository**: `zag23/rag-app`
- **Tag**: `latest`
- **Pull command**: `docker pull zag23/rag-app:latest`

## License

APACHE 2.0
