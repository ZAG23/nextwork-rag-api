FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py embed.py k8s.txt ./

# Embed initial documents
RUN python embed.py

EXPOSE 8000

# Default environment variables for Docker
# Use host.docker.internal on Mac/Windows, or set via -e
# Note: Ollama client expects hostname:port format, not URL
ENV OLLAMA_HOST=host.docker.internal:11434
ENV OLLAMA_MODEL=tinyllama
ENV CHROMA_DB_PATH=./db
ENV CHROMA_COLLECTION_NAME=docs

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
