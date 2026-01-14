# Restarting RAG API in Minikube

## Quick Restart Commands

### Method 1: Restart Deployment (Recommended)
```bash
kubectl rollout restart deployment rag-app-deployment
```

### Method 2: Delete Pod (Auto-recreates)
```bash
# Get pod name
POD_NAME=$(kubectl get pods -l app=rag-app -o jsonpath='{.items[0].metadata.name}')

# Delete pod (Kubernetes will automatically recreate it)
kubectl delete pod $POD_NAME
```

### Method 3: Scale Down/Up
```bash
# Scale down to 0
kubectl scale deployment rag-app-deployment --replicas=0

# Scale back up to 1
kubectl scale deployment rag-app-deployment --replicas=1
```

## Check Status

```bash
# Check deployment status
kubectl get deployment rag-app-deployment

# Check pod status
kubectl get pods -l app=rag-app

# Check service
kubectl get service rag-api-service

# View logs
kubectl logs -l app=rag-app --tail=50 -f
```

## Access the API

After restart, access via:
```bash
# Start minikube tunnel (if not already running)
minikube service rag-api-service

# Or access directly via NodePort
curl http://192.168.49.2:30001/
```

## Current Setup

- **Deployment**: `rag-app-deployment`
- **Service**: `rag-api-service` (NodePort, port 30001)
- **Namespace**: `default`
- **Minikube URL**: `http://127.0.0.1:53044` (via tunnel) or `http://192.168.49.2:30001` (direct)

## Troubleshooting

If the API doesn't restart properly:

1. **Check pod status**:
   ```bash
   kubectl describe pod -l app=rag-app
   ```

2. **Check events**:
   ```bash
   kubectl get events --sort-by='.lastTimestamp' | grep rag-app
   ```

3. **Force delete and recreate**:
   ```bash
   kubectl delete deployment rag-app-deployment
   # Then redeploy using your original deployment command
   ```
