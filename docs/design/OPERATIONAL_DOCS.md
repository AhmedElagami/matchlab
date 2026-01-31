# Operational Documentation

## Deployment

### Prerequisites

- Docker and Docker Compose
- At least 2GB RAM available

### Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd matchlab
   ```

2. Start services:
   ```bash
   docker-compose up -d
   ```

3. Run migrations:
   ```bash
   docker-compose exec app python manage.py migrate
   ```

4. Create superuser:
   ```bash
   docker-compose exec app python manage.py createsuperuser
   ```

5. Access the application at http://localhost:8000

## Environment Variables

Required environment variables:

- `DJANGO_SECRET_KEY`: Secret key for Django application
- `POSTGRES_DB`: PostgreSQL database name
- `POSTGRES_USER`: PostgreSQL user
- `POSTGRES_PASSWORD`: PostgreSQL password
- `POSTGRES_HOST`: PostgreSQL host
- `POSTGRES_PORT`: PostgreSQL port

## Database Operations

### Backup

```bash
docker-compose exec db pg_dump -U matchlab matchlab > backup.sql
```

### Restore

```bash
docker-compose exec -T db psql -U matchlab matchlab < backup.sql
```

## Testing

### Run Unit Tests

```bash
docker-compose exec app pytest
```

### Run E2E Tests

```bash
docker-compose run test
```

## Monitoring

### Logs

```bash
docker-compose logs -f app
docker-compose logs -f db
```

### Health Check

Endpoint: `GET /healthz/`

Response:
- 200 OK: Service is healthy
- 503 Service Unavailable: Service is unhealthy

## Performance

- Recommended maximum cohort size: 30 participants
- OR-Tools time limits:
  - Strict mode: 5 seconds
  - Exception mode: 10 seconds

## Security

- Always set `DEBUG=False` in production
- Use strong secret key in production
- Ensure HTTPS is enabled in production
- Regular security updates for dependencies