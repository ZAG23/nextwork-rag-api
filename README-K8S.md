# Kubernetes Deployment Guide

## Issues Fixed

1. **Image Name**: Changed from `rag-app` to `zag23/rag-app:latest` (or use `rag-app:latest` with `imagePullPolicy: Never` for local images)
2. **OLLAMA_HOST**: For minikube, use `host.docker.internal:11434` with `hostNetwork: true` to access host machine's Ollama
3. **Port Configuration**: Fixed port mismatch - application runs on port 8000 (not 5000) to match Dockerfile
4. **Host Network**: Added `hostNetwork: true` for minikube to allow pods to access host machine services
5. **Health Checks**: Added liveness and readiness probes on correct port (8000)
6. **Persistent Storage**: Added PVC for ChromaDB data persistence
7. **Service**: Created Service to expose the deployment with correct targetPort (8000)
8. **Resources**: Added resource requests and limits

## Deployment Steps

### 1. Configure Ollama Connection

**Option A: Ollama running in Kubernetes cluster (Production)**
```bash
# Create an Ollama service (if not exists)
kubectl create service clusterip ollama-service --tcp=11434:11434
# Then update deployment.yaml OLLAMA_HOST to: "ollama-service.default.svc.cluster.local:11434"
# Remove hostNetwork: true for production deployments
```

**Option B: Ollama running on host machine (Minikube/Local Dev) - RECOMMENDED**
```yaml
# In deployment.yaml, add to spec.template.spec:
hostNetwork: true
# And set OLLAMA_HOST to: "host.docker.internal:11434"
# This allows the pod to access Ollama running on your host machine
```

**Option C: Ollama running on external host**
```yaml
# Set OLLAMA_HOST to the external IP/hostname: "your-host-ip:11434"
# May require network configuration to allow pod-to-host communication
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
# Or if using SSH port forwarding, use the forwarded port (e.g., 63088)
```

## Accessing the API

After port forwarding:
- API: http://localhost:8000 (or your forwarded port)
- Docs: http://localhost:8000/docs

### Example API Calls

**Add knowledge:**
```bash
curl -X POST "http://localhost:8000/add" \
  -H "Content-Type: application/json" \
  -d '{"text": "Kubernetes is an open-source container orchestration platform..."}'
```

**Query knowledge:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"q": "What is Kubernetes?"}'
```

> **Important:** Always use JSON format with `Content-Type: application/json` header. Do not use `-G` flag with `--data-urlencode`.

## Troubleshooting

### Pod won't start
```bash
kubectl describe pod -l app=rag-api
kubectl logs -l app=rag-api
```

### Can't connect to Ollama
- Verify Ollama is running on host: `curl http://localhost:11434/api/tags`
- For minikube, verify host.docker.internal works: `minikube ssh "curl http://host.docker.internal:11434/api/tags"`
- Check OLLAMA_HOST environment variable: `kubectl exec <pod-name> -- env | grep OLLAMA`
- Verify hostNetwork is enabled: `kubectl get pod <pod-name> -o jsonpath='{.spec.hostNetwork}'`
- Test connection from pod: `kubectl exec <pod-name> -- curl -s http://host.docker.internal:11434/api/tags`
- Check pod logs for connection errors: `kubectl logs <pod-name>`

### PVC issues
```bash
kubectl get pvc
kubectl describe pvc chromadb-pvc
```

### Image pull issues
- If using local image: Set `imagePullPolicy: Never` and ensure image is built locally
- If using Docker Hub: Ensure `imagePullPolicy: IfNotPresent` or `Always`

### Port configuration issues
- Verify container port matches application port (should be 8000)
- Check service targetPort matches containerPort (should be 8000)
- Verify health check ports match application port (should be 8000)
- Check deployment: `kubectl get deployment rag-app-deployment -o yaml | grep -A 5 ports`
