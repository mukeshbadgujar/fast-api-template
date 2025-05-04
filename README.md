# FastAPI Template

A production-grade FastAPI template for building scalable, maintainable, and testable applications with built-in fallback mechanisms.

## Features

- 🚀 **Production-Ready**: Built with scalability and maintainability in mind
- 🧪 **TDD-First**: Comprehensive testing setup with pytest
- 🔄 **Multi-Environment**: Support for dev, UAT, and production environments
- 📊 **Observability**: Built-in metrics, tracing, and logging
- 🔒 **Security**: JWT authentication and role-based access control
- 🗄️ **Database**: SQLAlchemy + Alembic with automatic SQLite fallback
- 🔄 **Caching**: Redis integration with in-memory fallback
- 🚦 **Task Queue**: Celery with in-memory fallback
- 📝 **Documentation**: Auto-generated OpenAPI docs
- 🐳 **Containerized**: Docker and docker-compose support
- 🔄 **CI/CD**: GitHub Actions pipeline
- 🛡️ **Resilience**: Automatic fallback mechanisms for all critical services
- 📈 **Monitoring**: Prometheus + Grafana integration

## Project Structure

```
fastapi-template/
├── app/                       # Application code
│   ├── main.py                # ASGI entrypoint
│   ├── core/                  # Core functionality
│   │   ├── settings.py        # Pydantic Settings (env)
│   │   ├── logging.py         # Structured logging setup
│   │   ├── security.py        # JWT, OAuth2 schemes, CORS
│   │   ├── cache.py           # Redis cache with fallback
│   │   ├── tasks.py           # Celery tasks with fallback
│   │   └── events.py          # Startup/shutdown handlers
│   ├── db/                    # Database layer
│   │   ├── base.py            # Base model class (declarative)
│   │   ├── session.py         # SessionLocal, engine, fallback logic
│   │   └── migrations/        # Alembic env and versions
│   ├── domains/               # Domain-driven subpackages
│   │   ├── users/             # User domain package
│   │   │   ├── router.py      # APIRouter for /users  
│   │   │   ├── schemas.py     # Pydantic models for requests/responses
│   │   │   ├── models.py      # SQLAlchemy definitions
│   │   │   ├── service.py     # Business logic  
│   │   │   ├── repository.py  # DB access abstraction  
│   │   │   └── dependencies.py # fastapi.Depends helpers
│   │   └── health/            # Health check domain
│   ├── api/                   # Global API setup
│   │   ├── deps.py            # Common dependencies  
│   │   └── router.py          # Main router including all domains
│   ├── middleware/            # Custom middlewares                      
│   ├── tasks/                 # Background tasks with Celery 
│   └── utils/                 # Shared utilities, e.g. pagination
├── tests/                     # Test suite mirroring app structure
├── docs/                      # Documentation
├── scripts/                   # Utility scripts
├── alembic/                   # Database migrations
├── prometheus.yml             # Prometheus configuration
└── docker-compose.yml         # Service orchestration
```

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fastapi-template.git
cd fastapi-template
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start the development environment:
```bash
docker-compose up -d
```

4. Run migrations:
```bash
docker-compose exec app alembic upgrade head
```

5. Access the services:
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Flower (Celery): http://localhost:5555

## Development

### Running Tests
```bash
docker-compose exec app pytest
```

### Code Quality
```bash
docker-compose exec app black .
docker-compose exec app isort .
docker-compose exec app flake8
```

### Running the Application Locally
If you prefer to run the application without Docker:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your local configuration
```

3. Run the application:
```bash
python run.py
```

The application will automatically:
- Try to connect to PostgreSQL, fall back to SQLite if unavailable
- Use Redis for caching, fall back to in-memory cache if unavailable
- Use Celery for task queue, fall back to in-memory queue if unavailable

### Database Migrations
```bash
# Create a new migration
docker-compose exec app alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec app alembic upgrade head
```

### Fallback Mechanisms

The application includes automatic fallback mechanisms for critical services:

1. **Database Fallback**:
   - Primary: PostgreSQL
   - Fallback: SQLite
   - Configure with `DB_FALLBACK=true` in `.env`

2. **Cache Fallback**:
   - Primary: Redis
   - Fallback: In-memory cache
   - Configure with `REDIS_FALLBACK=true` in `.env`

3. **Task Queue Fallback**:
   - Primary: Celery
   - Fallback: In-memory queue
   - Configure with `CELERY_FALLBACK=true` in `.env`

### Monitoring

The application includes comprehensive monitoring:

1. **Prometheus Metrics**:
   - Application metrics at `/metrics`
   - Service health checks
   - Custom business metrics

2. **Grafana Dashboards**:
   - Pre-configured dashboards
   - Service health monitoring
   - Performance metrics

3. **Logging**:
   - JSON-formatted logs
   - Structured logging with context
   - Log levels configurable via environment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details