# Docker Deployment Guide

This guide provides quick instructions for running and debugging the DCA application using Docker Compose.

## Quick Start

1. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. Start services:
```bash
docker-compose up -d
```

3. Access services:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Flower Dashboard: http://localhost:5555
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Database Migrations

Use scripts for migrations operations:

```bash
python scripts/migrations.py upgrade
```

This command will upgrade the database schema to the latest version. Use this command to run migrations.

## Development Commands

### Basic Operations
```bash
# Start services
docker-compose up -d

# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f celery
docker-compose logs -f postgres

# Stop services
docker-compose down
```

