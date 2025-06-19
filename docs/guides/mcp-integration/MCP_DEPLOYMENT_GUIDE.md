# MCP Production Deployment Guide

Complete guide for deploying MCP servers in production environments using Docker and Kubernetes.

## Overview

This guide covers deploying MCP servers for production use with:
- Docker containerization for each MCP server
- Docker Compose for local/small deployments  
- Kubernetes manifests for scalable production
- Automated build and deployment scripts
- Monitoring and health checks

## Quick Start

### Docker Compose Deployment

```bash
# 1. Build MCP server images
./scripts/build_mcp_images.sh

# 2. Deploy with Docker Compose
cd docker
docker-compose -f docker-compose.mcp.yml up -d

# 3. Check status
docker-compose -f docker-compose.mcp.yml ps
```

### Kubernetes Deployment

```bash
# 1. Build and push images
./scripts/build_mcp_images.sh --push --registry your-registry.com

# 2. Update secrets in k8s/mcp-deployment.yaml
# 3. Deploy to Kubernetes
kubectl apply -f k8s/mcp-deployment-updated.yaml

# 4. Check status
kubectl get pods -n mcp-servers
```

## Docker Configuration

### Individual Dockerfiles

Each MCP server has its own optimized Dockerfile:

- **Perplexity MCP**: `docker/mcp-servers/perplexity/Dockerfile`
- **Xero MCP**: `docker/mcp-servers/xero/Dockerfile`  
- **Notion MCP**: `docker/mcp-servers/notion/Dockerfile`

Key features:
- Multi-stage builds for smaller images
- Non-root user for security
- Health checks for monitoring
- Proper signal handling for graceful shutdown

### Docker Compose Setup

The `docker/docker-compose.mcp.yml` provides:

- Service definitions for all MCP servers
- Environment variable configuration
- Network isolation with `mcp-network`
- Volume mounts for logs
- Health checks and restart policies
- Optional Nginx gateway for routing

### Environment Variables

Required environment variables for deployment:

```bash
# Core MCP servers
PERPLEXITY_API_KEY=your_perplexity_key
XERO_ACCESS_TOKEN=your_xero_token
XERO_CLIENT_ID=your_xero_client_id
XERO_CLIENT_SECRET=your_xero_secret
NOTION_API_KEY=your_notion_key

# Optional: Docker registry
DOCKER_REGISTRY=your-registry.com
IMAGE_TAG=latest
```

## Kubernetes Deployment

### Architecture

The Kubernetes deployment includes:

- **Namespace**: `mcp-servers` for isolation
- **Secrets**: Secure API key storage
- **Deployments**: One per MCP server with 2 replicas
- **Services**: Internal ClusterIP services
- **HPA**: Horizontal Pod Autoscaler for scaling
- **Resource limits**: CPU and memory constraints

### Scaling Configuration

Auto-scaling based on:
- CPU utilization: Scale when >70%
- Memory utilization: Scale when >80%
- Min replicas: 1 per service
- Max replicas: 5 per service

### Security Features

- Non-root containers
- Resource limits and requests
- Secret-based credential management
- Network policies (optional)
- Pod security policies (optional)

## Build and Deployment Scripts

### Build Script Features

The `scripts/build_mcp_images.sh` script provides:

```bash
# Basic build
./scripts/build_mcp_images.sh

# Build and push to registry
./scripts/build_mcp_images.sh --push --registry your-registry.com

# Build, test, and cleanup
./scripts/build_mcp_images.sh --test --cleanup

# Custom tag
./scripts/build_mcp_images.sh --tag v1.2.3
```

Features:
- Builds Docker images for all MCP servers
- Pushes to configurable registry
- Generates deployment configurations
- Runs deployment tests
- Cleans up old images

### Deployment Workflow

1. **Build Phase**
   - Clone MCP repositories within containers
   - Install dependencies and build
   - Create optimized container images
   - Tag with version/latest

2. **Test Phase**
   - Start services with Docker Compose
   - Verify health checks pass
   - Test basic connectivity
   - Clean up test environment

3. **Deploy Phase**
   - Push images to registry
   - Update Kubernetes manifests
   - Apply to cluster
   - Monitor rollout status

## Monitoring and Health Checks

### Container Health Checks

Each container includes:
- **Liveness probes**: Restart unhealthy containers
- **Readiness probes**: Control traffic routing
- **Startup probes**: Handle slow initialization

### Service Monitoring

Monitor these metrics:
- Container restart counts
- Resource utilization (CPU/Memory)
- Request latency and error rates
- MCP protocol errors

### Log Aggregation

Logs are available via:
- Docker: `docker logs <container-name>`
- Kubernetes: `kubectl logs -n mcp-servers <pod-name>`
- Persistent volumes for log retention

## Production Best Practices

### Security

1. **Secrets Management**
   ```bash
   # Kubernetes secrets
   kubectl create secret generic mcp-secrets \
     --from-literal=perplexity-api-key=YOUR_KEY \
     --from-literal=xero-access-token=YOUR_TOKEN \
     -n mcp-servers
   ```

2. **Network Policies**
   - Restrict inter-service communication
   - Limit external access
   - Use TLS for service-to-service

3. **Container Security**
   - Regular base image updates
   - Vulnerability scanning
   - Non-root execution
   - Resource constraints

### Performance

1. **Resource Planning**
   ```yaml
   resources:
     requests:
       memory: "128Mi"
       cpu: "100m"
     limits:
       memory: "512Mi"
       cpu: "500m"
   ```

2. **Scaling Strategy**
   - Horizontal Pod Autoscaler (HPA)
   - Vertical Pod Autoscaler (VPA) for right-sizing
   - Cluster autoscaling for node management

3. **Caching**
   - Redis for MCP response caching
   - CDN for static assets
   - Connection pooling

### Reliability

1. **High Availability**
   - Multi-zone deployment
   - Pod disruption budgets
   - Rolling updates with zero downtime

2. **Backup and Recovery**
   - Configuration backups
   - Disaster recovery procedures
   - Data persistence strategies

3. **Circuit Breakers**
   - Timeout configurations
   - Retry logic with exponential backoff
   - Graceful degradation

## Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check container logs
docker logs <container-name>

# Kubernetes logs
kubectl logs -n mcp-servers <pod-name>

# Check resource constraints
kubectl describe pod -n mcp-servers <pod-name>
```

#### Connection Issues
```bash
# Test service connectivity
kubectl exec -it -n mcp-servers <pod-name> -- wget -qO- http://service-name:port/health

# Check service endpoints
kubectl get endpoints -n mcp-servers

# Verify network policies
kubectl get networkpolicies -n mcp-servers
```

#### Performance Issues
```bash
# Check resource usage
kubectl top pods -n mcp-servers

# Review HPA status
kubectl get hpa -n mcp-servers

# Analyze metrics
kubectl get --raw /apis/metrics.k8s.io/v1beta1/namespaces/mcp-servers/pods
```

### Debug Mode

Enable debug logging:

```bash
# Docker Compose
DEBUG=mcp:* docker-compose -f docker-compose.mcp.yml up

# Kubernetes
kubectl set env deployment/perplexity-mcp DEBUG=mcp:* -n mcp-servers
```

### Health Check Endpoints

Each service exposes health endpoints:
- Liveness: `GET /health/live`
- Readiness: `GET /health/ready`
- Metrics: `GET /metrics` (if enabled)

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy MCP Servers

on:
  push:
    branches: [main]
    paths: ['mcp/**', 'docker/**', 'k8s/**']

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build MCP Images
      run: |
        ./scripts/build_mcp_images.sh \
          --registry ${{ secrets.DOCKER_REGISTRY }} \
          --tag ${{ github.sha }} \
          --push
    
    - name: Deploy to Kubernetes
      run: |
        kubectl apply -f k8s/mcp-deployment-updated.yaml
        kubectl rollout status deployment/perplexity-mcp -n mcp-servers
```

### GitLab CI Example

```yaml
stages:
  - build
  - test  
  - deploy

build-mcp-images:
  stage: build
  script:
    - ./scripts/build_mcp_images.sh --registry $CI_REGISTRY --tag $CI_COMMIT_SHA
  only:
    changes:
      - mcp/**/*
      - docker/**/*

deploy-production:
  stage: deploy
  script:
    - kubectl apply -f k8s/mcp-deployment-updated.yaml
  environment:
    name: production
  only:
    - main
```

## Cost Optimization

### Resource Right-Sizing

Monitor and adjust:
- CPU requests and limits
- Memory allocation
- Storage requirements
- Network bandwidth

### Scaling Policies

Configure appropriate:
- Minimum replica counts
- Maximum replica counts
- Scale-up/down thresholds
- Cooldown periods

### Cost Monitoring

Track costs by:
- Service/team labels
- Resource utilization
- Scaling events
- Storage usage

## Next Steps

1. **Advanced Monitoring**
   - Implement Prometheus metrics
   - Set up Grafana dashboards
   - Configure AlertManager rules

2. **Service Mesh**
   - Consider Istio for traffic management
   - Implement distributed tracing
   - Add mutual TLS

3. **GitOps Deployment**
   - ArgoCD for continuous deployment
   - Flux for Git-based workflows
   - Helm charts for templating

4. **Multi-Region Deployment**
   - Cross-region replication
   - Disaster recovery procedures
   - Global load balancing

For additional information:
- [MCP Setup Guide](./MCP_SETUP_GUIDE.md)
- [MCP Testing Framework](./MCP_TESTING_FRAMEWORK.md)
- [Troubleshooting Guide](./MCP_TROUBLESHOOTING.md)