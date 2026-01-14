# Kubernetes Deployment Guide

## Quick Deploy

### Option 1: Simple Deployment (All env vars in YAML)
```bash
kubectl apply -f k8s-deployment.yaml
```

### Option 2: Using ConfigMap (Recommended for production)
```bash
# Create ConfigMap first
kubectl apply -f k8s-configmap.yaml

# Then deploy
kubectl apply -f k8s-deployment-with-configmap.yaml
```

## Update Existing Deployment

To update your existing deployment with new environment variables:

```bash
# Method 1: Patch the deployment
kubectl set env deployment/rag-app-deployment \
  OLLAMA_MODEL=tinyllama \
  CHROMA_DB_PATH=/app/db \
  CHROMA_COLLECTION_NAME=docs

# Method 2: Edit directly
kubectl edit deployment rag-app-deployment
# Then add the env vars in the containers section
```

## Environment Variables

The deployment now supports these environment variables:

- `OLLAMA_HOST`: Ollama server address (default: `host.docker.internal:11434`)
- `OLLAMA_MODEL`: Model to use (default: `tinyllama`)
- `CHROMA_DB_PATH`: Database path (default: `/app/db`)
- `CHROMA_COLLECTION_NAME`: Collection name (default: `docs`)

## Access the API

After deployment:

```bash
# Start minikube tunnel
minikube service rag-api-service

# Or access via NodePort
curl http://192.168.49.2:30001/
```

## Update Deployment

After updating the Docker image or code:

```bash
# Restart deployment
kubectl rollout restart deployment rag-app-deployment

# Or update image
kubectl set image deployment/rag-app-deployment rag-api-container=zag23/rag-app:latest

# Check rollout status
kubectl rollout status deployment rag-app-deployment
```
