import uuid
import os
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import chromadb
from ollama import Client

app = FastAPI(
    title="Nextwork RAG API",
    description="A RAG (Retrieval-Augmented Generation) API using ChromaDB and Ollama",
    version="1.0.0"
)

# Configuration from environment variables
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "docs")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "tinyllama")
OLLAMA_HOST_RAW = os.getenv("OLLAMA_HOST", "localhost:11434")

# Initialize ChromaDB client and collection
try:
    chroma = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = chroma.get_or_create_collection(CHROMA_COLLECTION_NAME)
except Exception as e:
    raise RuntimeError(
        f"Failed to initialize ChromaDB at path '{CHROMA_DB_PATH}': {str(e)}. "
        f"Ensure the directory exists and is writable."
    )

# Initialize Ollama client
# Parse OLLAMA_HOST - client expects hostname:port format, not URL
ollama_host = OLLAMA_HOST_RAW.replace("http://", "").replace("https://", "")
try:
    ollama_client = Client(host=ollama_host)
    # Test connection by checking available models
    models = ollama_client.list()
    model_names = [m.name for m in models.models] if hasattr(models, 'models') else []
    if OLLAMA_MODEL not in model_names:
        print(f"Warning: Model '{OLLAMA_MODEL}' not found in Ollama. Available models: {model_names}")
except Exception as e:
    print(f"Warning: Could not connect to Ollama at {ollama_host}: {str(e)}")
    print("The API will start but queries may fail. Ensure Ollama is running and accessible.")


class QueryRequest(BaseModel):
    q: str
    n_results: int = 1  # Number of results to return (default: 1, max: 10)
    include_scores: bool = False  # Whether to include relevance scores
    use_best_only: bool = True  # If True, only use best result for AI answer; if False, combine all results


class AddRequest(BaseModel):
    text: str


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Nextwork RAG API is running"}


@app.post("/add", status_code=status.HTTP_201_CREATED)
def add_knowledge(request: AddRequest):
    """Add new content to the knowledge base dynamically."""
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty. Please provide non-empty text content."
        )
    
    try:
        # Generate a unique ID for this document
        doc_id = str(uuid.uuid4())
        
        # Add the text to Chroma collection
        collection.add(documents=[request.text], ids=[doc_id])
        
        return {
            "status": "success",
            "message": "Content added to knowledge base",
            "id": doc_id
        }
    except chromadb.errors.InvalidDimensionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid document format: {str(e)}. This may occur if the collection has existing documents with different embedding dimensions."
        )
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "network" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database connection error: {error_msg}. Check if ChromaDB is accessible and the database path '{CHROMA_DB_PATH}' is correct."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add content: {error_msg}"
        )


@app.post("/query")
def query(request: QueryRequest):
    """
    Query the knowledge base and get an AI-generated answer.
    
    Supports multiple results and relevance scores for better context retrieval.
    """
    if not request.q or not request.q.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty. Please provide a question to search the knowledge base."
        )
    
    # Validate n_results
    if request.n_results < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="n_results must be at least 1"
        )
    if request.n_results > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="n_results cannot exceed 10 for performance reasons"
        )
    
    try:
        # Query ChromaDB for relevant context
        results = collection.query(
            query_texts=[request.q],
            n_results=request.n_results,
            include=["documents", "distances", "metadatas"]
        )
        
        # Extract results
        documents = results.get("documents", [])
        distances = results.get("distances", [])
        metadatas = results.get("metadatas", [])
        ids = results.get("ids", [])
        
        if not documents or len(documents) == 0 or len(documents[0]) == 0:
            doc_count = collection.count()
            if doc_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No documents found in knowledge base. Add content using the /add endpoint first."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No relevant context found for your query. The knowledge base has {doc_count} document(s), but none match your question. Try rephrasing your query or adding more relevant content."
                )
        
        # Prepare results with metadata
        search_results = []
        for i in range(len(documents[0])):
            result_item = {
                "id": ids[0][i] if ids and len(ids) > 0 and len(ids[0]) > i else None,
                "text": documents[0][i],
            }
            if request.include_scores and distances and len(distances) > 0 and len(distances[0]) > i:
                # ChromaDB returns distances (lower is better), convert to similarity score
                distance = distances[0][i]
                similarity = 1.0 / (1.0 + distance)  # Convert distance to similarity (0-1 scale)
                result_item["relevance_score"] = round(similarity, 4)
                result_item["distance"] = round(distance, 4)
            if metadatas and len(metadatas) > 0 and len(metadatas[0]) > i:
                result_item["metadata"] = metadatas[0][i]
            search_results.append(result_item)
        
        # Prepare context for AI generation
        if request.use_best_only:
            # Use only the best (first) result
            context = search_results[0]["text"]
        else:
            # Combine all results
            context = "\n\n".join([f"[Result {i+1}]: {r['text']}" for i, r in enumerate(search_results)])
        
        # Generate answer using Ollama
        try:
            answer = ollama_client.generate(
                model=OLLAMA_MODEL,
                prompt=f"Context:\n{context}\n\nQuestion: {request.q}\n\nAnswer clearly and concisely:"
            )
            
            # Build response
            response = {
                "answer": answer.response,
                "results_count": len(search_results)
            }
            
            if request.include_scores or not request.use_best_only:
                response["results"] = search_results
            
            return response
        except Exception as ollama_error:
            error_msg = str(ollama_error)
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Cannot connect to Ollama at {ollama_host}. Ensure Ollama is running and accessible. Error: {error_msg}"
                )
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Model '{OLLAMA_MODEL}' not found in Ollama. Install it with: ollama pull {OLLAMA_MODEL}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ollama generation failed: {error_msg}"
                )
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "network" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database connection error: {error_msg}. Check if ChromaDB is accessible."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {error_msg}"
        )


@app.delete("/delete/{doc_id}", status_code=status.HTTP_200_OK)
def delete_document(doc_id: str):
    """Delete a document from the knowledge base by ID."""
    if not doc_id or not doc_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document ID cannot be empty"
        )
    
    try:
        # Check if document exists
        try:
            results = collection.get(ids=[doc_id])
            if not results["ids"] or len(results["ids"]) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Document with ID '{doc_id}' not found in the knowledge base."
                )
        except HTTPException:
            raise
        except Exception as e:
            # If get fails, try delete anyway (idempotent operation)
            pass
        
        # Delete the document
        collection.delete(ids=[doc_id])
        
        return {
            "status": "success",
            "message": f"Document '{doc_id}' deleted successfully",
            "id": doc_id
        }
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "connection" in error_msg.lower() or "network" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Database connection error: {error_msg}. Check if ChromaDB is accessible."
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {error_msg}"
        )
