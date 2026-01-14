#!/bin/bash

echo "=== Docker Containers (with uptime) ==="
docker ps --filter "name=rag-app" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

echo ""
echo "=== Kubernetes Pods (with age/uptime) ==="
kubectl get pods -l app=rag-api 2>/dev/null || kubectl get pods | grep rag-api || echo "No Kubernetes pods found or kubectl not configured"

echo ""
echo "=== All Docker Images (no uptime - images don't run) ==="
docker images | grep rag-app || echo "No rag-app images found"
