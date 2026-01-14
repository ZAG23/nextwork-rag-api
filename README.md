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
  "q": "What is Kubernetes?"
}
```

**Response:**
```json
{
  "answer": "Kubernetes is a container orchestration platform..."
}
```

## Usage Examples

### Using cURL

**Add content:**
```bash
curl -X POST "http://localhost:8000/add" \
  -H "Content-Type: application/json" \
  -d '{"text": "FastAPI is a modern web framework for building APIs with Python."}'
```

**Query:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"q": "What is FastAPI?"}'
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

# Query
response = requests.post(
    "http://localhost:8000/query",
    json={"q": "Your question here"}
)
print(response.json()["answer"])
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

- **Database Path**: The ChromaDB database is stored in `./db` (can be changed in `app.py` line 15)
- **Ollama Model**: Default is `tinyllama` (can be changed in `app.py` line 95)
- **Collection Name**: Default is `"docs"` (can be changed in `app.py` line 16)
- **Ollama Host**: 
  - Local development: Defaults to `localhost:11434`
  - Docker: Set via `OLLAMA_HOST` environment variable (defaults to `host.docker.internal:11434`)
  - The code automatically strips `http://` or `https://` prefixes if present

### Environment Variables

- `OLLAMA_HOST`: Ollama server address in `hostname:port` format (e.g., `localhost:11434` or `host.docker.internal:11434`)
  - **Note**: The Ollama Python client expects `hostname:port` format, not a full URL. Protocol prefixes are automatically removed.

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

- **Fixed Ollama client response handling**: Changed from dictionary access (`answer["response"]`) to attribute access (`answer.response`) to match the Ollama Python client API
- **Improved Ollama host configuration**: Added automatic protocol stripping for `OLLAMA_HOST` environment variable to handle both URL and hostname:port formats
- **Docker support**: Added Dockerfile and published image to Docker Hub (`zag23/rag-app:latest`)
- **Connection testing**: Added `test_connection.py` script to verify Ollama and ChromaDB connections
- **Error handling**: Improved error messages and exception handling

### Docker Hub

The working image is available on Docker Hub:
- **Repository**: `zag23/rag-app`
- **Tag**: `latest`
- **Pull command**: `docker pull zag23/rag-app:latest`

## License

APACHE 2.0
