# Financial Forecast Agent - Production Deployment Guide

## Overview

This guide provides instructions for deploying the Financial Forecast Agent to production with Docker containers, monitoring, and security best practices.

## Prerequisites

### Required Environment Variables

Create a `.env` file in the parent directory (`../`) with:

```bash
# OpenAI & LangChain
OPENAI_API_KEY="your_openai_api_key"
LANGCHAIN_API_KEY="your_langchain_api_key"
LANGCHAIN_TRACING_V2=true

# Xero API
XERO_ACCESS_TOKEN="your_xero_access_token"
XERO_CLIENT_ID="your_xero_client_id"
XERO_CLIENT_SECRET="your_xero_client_secret"
XERO_REDIRECT_URI="http://localhost:8080/callback"

# Perplexity API
PERPLEXITY_API_KEY="your_perplexity_api_key"

# Notion API
NOTION_API_KEY="your_notion_api_key"
```

### System Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 2 CPU cores minimum
- 10GB disk space

## Quick Start

1. **Validate Environment**
   ```bash
   # Ensure all API keys are set
   ./deploy-production.sh
   ```

2. **Monitor Deployment**
   ```bash
   # Check service health
   curl http://localhost:80/health
   
   # View logs
   docker-compose -f docker-compose.production.yml logs -f
   ```

3. **Access Services**
   - Agent API: http://localhost:80
   - Health Check: http://localhost:80/health
   - Monitoring: http://localhost:9090
   - Metrics: http://localhost:80/metrics

## Production Architecture

### Services

1. **Financial Forecast Agent** (`forecast-agent`)
   - Main application container
   - Ports: 8000 (internal), 8080 (OAuth callback)
   - Resource limits: 4GB RAM, 2 CPU cores
   - Health checks every 30s

2. **Nginx Reverse Proxy** (`nginx`)
   - SSL termination and rate limiting
   - Ports: 80 (HTTP), 443 (HTTPS)
   - Rate limit: 10 requests/minute per IP

3. **Prometheus Monitoring** (`prometheus`)
   - Metrics collection and alerting
   - Port: 9090
   - Scrapes agent metrics every 30s

4. **Database Storage** (`forecast-db`)
   - Persistent SQLite storage
   - Volume: `forecast-data`

### Security Features

- **Rate Limiting**: 10 requests/minute per IP
- **Security Headers**: HSTS, X-Frame-Options, etc.
- **Non-root Container**: Agent runs as user `agent` (UID 1000)
- **Resource Limits**: CPU and memory constraints
- **Health Checks**: Automatic container restart on failure

## Configuration

### Resource Limits

Adjust in `docker-compose.production.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '0.5'
      memory: 1G
```

### SSL/HTTPS Setup

1. **Generate SSL Certificates**
   ```bash
   # Self-signed for testing
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout ssl/key.pem -out ssl/cert.pem
   ```

2. **Update Nginx Config**
   Uncomment HTTPS section in `nginx/nginx.conf`

3. **Update Domain**
   Replace `your-domain.com` with your actual domain

### Monitoring Setup

**Prometheus Targets** (in `monitoring/prometheus.yml`):
- Agent health: `forecast-agent:8000/health`
- Agent metrics: `forecast-agent:8000/metrics`

**Custom Alerts** (create `monitoring/alerts.yml`):
```yaml
groups:
  - name: forecast_agent
    rules:
      - alert: AgentDown
        expr: up{job="financial-forecast-agent"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Financial Forecast Agent is down"
```

## Deployment Commands

### Start Production
```bash
./deploy-production.sh
```

### Stop Production
```bash
./stop-production.sh
```

### View Status
```bash
docker-compose -f docker-compose.production.yml ps
```

### View Logs
```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f forecast-agent
```

### Scale Services
```bash
# Scale agent instances
docker-compose -f docker-compose.production.yml up -d --scale forecast-agent=3
```

## API Usage

### Health Check
```bash
curl http://localhost:80/health
```

### Run Forecast
```bash
curl -X POST http://localhost:80/forecast \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_123"}'
```

### Get Metrics
```bash
curl http://localhost:80/metrics
```

## Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```bash
   # Check logs
   docker-compose -f docker-compose.production.yml logs forecast-agent
   
   # Check environment variables
   docker-compose -f docker-compose.production.yml exec forecast-agent env
   ```

2. **Health Check Failing**
   ```bash
   # Test health endpoint directly
   docker-compose -f docker-compose.production.yml exec forecast-agent curl localhost:8000/health
   ```

3. **API Keys Invalid**
   ```bash
   # Validate environment
   docker-compose -f docker-compose.production.yml exec forecast-agent python -c "import os; print(os.getenv('OPENAI_API_KEY')[:10])"
   ```

### Log Locations

- Application logs: `./logs/`
- Container logs: `docker-compose logs`
- Nginx logs: `/var/log/nginx/` (inside nginx container)

## Backup & Recovery

### Database Backup
```bash
# Backup SQLite database
docker-compose -f docker-compose.production.yml exec forecast-db tar -czf /data/backup-$(date +%Y%m%d).tar.gz /data/*.db
```

### Configuration Backup
```bash
# Backup configuration
tar -czf config-backup-$(date +%Y%m%d).tar.gz nginx/ monitoring/ docker-compose.production.yml
```

## Security Considerations

1. **Change Default Ports** in production
2. **Use SSL/TLS** for external access
3. **Restrict Metrics Access** to internal networks
4. **Rotate API Keys** regularly
5. **Monitor Resource Usage** and set alerts
6. **Keep Images Updated** with security patches

## Performance Tuning

### High Load Configuration

```yaml
# In docker-compose.production.yml
deploy:
  replicas: 3
  resources:
    limits:
      cpus: '4.0'
      memory: 8G
```

### Database Optimization

```bash
# Use external PostgreSQL for high volume
# Replace SQLite with PostgreSQL service
```

## Maintenance

### Updates
```bash
# Pull latest images
docker-compose -f docker-compose.production.yml pull

# Restart with new images
docker-compose -f docker-compose.production.yml up -d
```

### Cleanup
```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune
```

## Support

For issues and questions:
- Check logs first: `docker-compose logs`
- Verify environment variables
- Test API endpoints manually
- Review resource usage: `docker stats`