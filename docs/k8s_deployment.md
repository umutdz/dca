# Kubernetes Deployment Guide

This guide provides instructions for deploying the DCA application on Kubernetes, both locally and in production environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Production Deployment](#production-deployment)
- [Accessing Services](#accessing-services)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following tools installed:
- [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [Docker](https://docs.docker.com/get-docker/)
- [Helm](https://helm.sh/docs/intro/install/) (optional, for production)

## Local Development Setup

### 1. Create Local Cluster

We provide scripts for setting up a local Kubernetes environment using Kind:

```bash
# Create a Kind cluster
kind create cluster --name local-cluster --config kind-config.yaml

# Install NGINX Ingress Controller
kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml

# Wait for Ingress controller to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s
```

### 2. Setup Namespace and Dependencies

```bash
# Create local namespace
kubectl create namespace dca-local

# Create dependencies directory if it doesn't exist
mkdir -p .deployments/kubernetes/local/dependencies

# Deploy dependencies
kubectl apply -f .deployments/kubernetes/local/dependencies

# Apply configMap
kubectl apply -f .deployments/kubernetes/local
```

### 3. Build and Deploy Application

```bash
# Build app
docker build -t dca:latest -f compose/development/DockerfileApp .

# Load image to Kind cluster
kind load docker-image dca:latest --name local-cluster
```

### 4. Deploy Workers and Monitoring

```bash
# Deploy Celery workers
kubectl apply -f .deployments/kubernetes/local/workers

# Deploy Flower monitoring
kubectl apply -f .deployments/kubernetes/local/monitoring
```

## Production Deployment

For production deployment, we recommend using Helm charts. The deployment process includes:

1. Configure production values
2. Deploy using Helm
3. Set up monitoring and logging
4. Configure backup solutions

Detailed production deployment instructions will be added in a future update.

## Accessing Services

### Local Development

```bash
# Execute commands in a pod
kubectl exec -it $(kubectl get pod -n dca-local -l app=dca -o jsonpath='{.items[0].metadata.name}') -n dca-local -- bash

# Configure local hostname for testing
echo "127.0.0.1 local-api.local-cluster" | sudo tee -a /etc/hosts
cat /etc/hosts | grep local-api.local-cluster
```

### Service URLs

- API: `http://local-api.local-cluster`
- Flower Dashboard: `http://flower.local-cluster`
- Prometheus: `http://prometheus.local-cluster`
- Grafana: `http://grafana.local-cluster`

## Troubleshooting

### Common Issues

1. **Ingress Controller Not Ready**
   ```bash
   kubectl get pods -n ingress-nginx
   kubectl describe pod -n ingress-nginx -l app.kubernetes.io/component=controller
   ```

2. **Pod Startup Issues**
   ```bash
   kubectl get pods -n dca-local
   kubectl describe pod <pod-name> -n dca-local
   kubectl logs <pod-name> -n dca-local
   ```

3. **Service Connection Issues**
   ```bash
   kubectl get svc -n dca-local
   kubectl describe svc <service-name> -n dca-local
   ```

### Getting Help

If you encounter any issues not covered in this guide:
1. Check the application logs
2. Review the Kubernetes events
3. Open an issue on our GitHub repository

## Next Steps

- [ ] Add production deployment guide
- [ ] Include backup and restore procedures
- [ ] Add scaling guidelines
- [ ] Document monitoring and alerting setup
