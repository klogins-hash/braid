# Deployment Guide

This guide covers deploying your Braid agent to production environments.

## Quick Start

### Local Development
```bash
# Build and run locally
docker compose up --build

# View logs
docker compose logs -f agent

# Stop services
docker compose down
```

## Production Deployment

### Docker

#### Build Production Image
```bash
# Build optimized production image
docker build -t your-agent:latest .build/

# Run with production settings
docker run -d \
  --name your-agent \
  --env-file .env \
  --restart unless-stopped \
  your-agent:latest
```

#### Docker Compose (Recommended)
```bash
# Production deployment
docker compose -f docker-compose.yml up -d

# Scale if needed
docker compose up -d --scale agent=3
```

### Container Registry

#### Push to Registry
```bash
# Tag for registry
docker tag your-agent:latest your-registry.com/your-agent:latest

# Push to registry
docker push your-registry.com/your-agent:latest
```


## Environment Configuration

### Required Environment Variables
```bash
# Core LLM Configuration
OPENAI_API_KEY=your-openai-key
# ANTHROPIC_API_KEY=your-anthropic-key  # Alternative

# Tool-specific Configuration
# SLACK_BOT_TOKEN=your-slack-token
# GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/google-creds.json

# Optional Configuration
LOG_LEVEL=INFO
AGENT_MODEL=gpt-4o
AGENT_TEMPERATURE=0.1
```

### Security Best Practices

1. **Never commit secrets** to version control
2. **Use environment variables** for all sensitive data
3. **Rotate API keys** regularly
4. **Limit container permissions** (runs as non-root user)
5. **Use secrets management** in production (Kubernetes secrets, AWS Secrets Manager, etc.)

### Health Checks

The container includes health checks that verify:
- Python interpreter is working
- Core dependencies are importable
- Basic agent initialization succeeds

### Troubleshooting

#### Common Issues

**Container won't start:**
```bash
# Check logs
docker logs your-agent-container

# Run interactively for debugging
docker run -it --entrypoint /bin/bash your-agent:latest
```

**Missing environment variables:**
```bash
# Verify environment
docker exec your-agent-container env | grep -E "(OPENAI|SLACK|GOOGLE)"
```

**Import errors:**
```bash
# Check Python path
docker exec your-agent-container python -c "import sys; print(sys.path)"

# Test imports
docker exec your-agent-container python -c "import your_agent_module"
```

#### Performance Tuning

**Memory Usage:**
- Default limit: 512Mi
- Adjust based on your agent's requirements
- Monitor with `docker stats` or Kubernetes metrics

**CPU Usage:**
- Default limit: 500m (0.5 CPU cores)
- Scale horizontally for high throughput
- Consider async patterns for I/O heavy workloads

## Support

For issues with:
- **Braid toolkit**: Check the main repository documentation
- **Agent logic**: Review your agent's logs and configuration
- **Infrastructure**: Consult your platform's documentation (Docker, Kubernetes, etc.)
