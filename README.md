# FastAPI Template

A production-grade FastAPI template for building scalable, maintainable, and testable applications.

## Features

- 🚀 **Production-Ready**: Built with scalability and maintainability in mind
- 🧪 **TDD-First**: Comprehensive testing setup with pytest
- 🔄 **Multi-Environment**: Support for dev, UAT, and production environments
- 📊 **Observability**: Built-in metrics, tracing, and logging
- 🔒 **Security**: JWT authentication and role-based access control
- 🗄️ **Database**: SQLAlchemy + Alembic for database management
- 🔄 **Caching**: Redis integration for performance optimization
- 🚦 **Circuit Breakers**: Resilient external service integration
- 📝 **Documentation**: Auto-generated OpenAPI docs
- 🐳 **Containerized**: Docker and docker-compose support
- 🔄 **CI/CD**: GitHub Actions pipeline

## Project Structure

```
fastapi-template/
├── app/                    # Application code
│   ├── api/               # API routes
│   ├── core/              # Core functionality
│   ├── db/                # Database models and migrations
│   ├── services/          # Business logic
│   ├── schemas/           # Pydantic models
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── alembic/               # Database migrations
└── docker/                # Docker configuration
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

5. Run the application:
```bash
python run.py
```

6. Access the API:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

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
If you prefer to run the application without Docker, you can use the `run.py` script:

```bash
python run.py
```

Ensure that all dependencies are installed and the environment variables are properly configured before running the script.

### Database Migrations
```bash
# Create a new migration
docker-compose exec app alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec app alembic upgrade head
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details