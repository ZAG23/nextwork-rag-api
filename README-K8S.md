# Kubernetes Deployment Guide

## Issues Fixed

1. **Image Name**: Changed from `rag-app` to `zag23/rag-app:latest` (or use `rag-app:latest` with `imagePullPolicy: Never` for local images)
2. **OLLAMA_HOST**: `host.docker.internal` doesn't work in Kubernetes. Updated to use service name pattern
3. **Health Checks**: Added liveness and readiness probes
4. **Persistent Storage**: Added PVC for ChromaDB data persistence
5. **Service**: Created Service to expose the deployment
6. **Resources**: Added resource requests and limits

## Deployment Steps

### 1. Configure Ollama Connection

**Option A: Ollama running in Kubernetes cluster**
```bash
# Create an Ollama service (if not exists)
kubectl create service clusterip ollama-service --tcp=11434:11434
# Then update deployment.yaml OLLAMA_HOST to: "ollama-service.default.svc.cluster.local:11434"
```

**Option B: Ollama running on host machine (for local dev)**
```yaml
# In deployment.yaml, add to spec.template.spec:
hostNetwork: true
# And set OLLAMA_HOST to: "localhost:11434"
```

**Option C: Ollama running on external host**
```yaml
# Set OLLAMA_HOST to the external IP/hostname: "your-host-ip:11434"
```

### 2. Create Persistent Volume Claim
```bash
kubectl apply -f pvc.yaml
```

### 3. Deploy the Application
```bash
kubectl apply -f deployment.yaml
```

### 4. Create Service
```bash
kubectl apply -f service.yaml
```

### 5. Verify Deployment
```bash
# Check pods
kubectl get pods -l app=rag-api

# Check deployment
kubectl get deployment rag-app-deployment

# Check service
kubectl get service rag-api-service

# View logs
kubectl logs -l app=rag-api

# Port forward to test locally
kubectl port-forward service/rag-api-service 8000:80
```

## Accessing the API

After port forwarding:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Troubleshooting

### Pod won't start
```bash
kubectl describe pod -l app=rag-api
kubectl logs -l app=rag-api
```

### Can't connect to Ollama
- Verify Ollama is accessible from the pod
- Check OLLAMA_HOST environment variable
- Test connection: `kubectl exec -it <pod-name> -- curl http://<ollama-host>:11434/api/tags`

### PVC issues
```bash
kubectl get pvc
kubectl describe pvc chromadb-pvc
```

### Image pull issues
- If using local image: Set `imagePullPolicy: Never` and ensure image is built locally
- If using Docker Hub: Ensure `imagePullPolicy: IfNotPresent` or `Always`
