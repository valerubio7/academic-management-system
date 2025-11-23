.PHONY: help migrate makemigrations collectstatic test shell logs clean build up down restart deploy check-env

# Default target
help:
	@echo "Academic Management System - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make up              - Start development environment"
	@echo "  make down            - Stop development environment"
	@echo "  make restart         - Restart development environment"
	@echo "  make logs            - View application logs"
	@echo "  make shell           - Open Django shell"
	@echo "  make test            - Run test suite"
	@echo ""
	@echo "Database:"
	@echo "  make migrate         - Apply database migrations"
	@echo "  make makemigrations  - Create new migrations"
	@echo ""
	@echo "Static Files:"
	@echo "  make collectstatic   - Collect static files for production"
	@echo ""
	@echo "Production:"
	@echo "  make build-prod      - Build production Docker image"
	@echo "  make deploy-prod     - Deploy to production"
	@echo "  make check-env       - Validate environment configuration"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean           - Clean temporary files and caches"

# Development Environment
up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f backend

shell:
	docker compose exec backend python manage.py shell

# Database Management
migrate:
	docker compose exec backend python manage.py migrate

makemigrations:
	docker compose exec backend python manage.py makemigrations

# Static Files
collectstatic:
	docker compose exec backend python manage.py collectstatic --noinput

# Testing
test:
	docker compose exec backend python manage.py test

test-coverage:
	docker compose exec backend coverage run --source='.' manage.py test
	docker compose exec backend coverage report
	docker compose exec backend coverage html

# Production Deployment
build-prod:
	docker compose -f docker-compose.prod.yml build

deploy-prod: check-env
	@echo "Deploying to production..."
	docker compose -f docker-compose.prod.yml up -d
	@echo "Running migrations..."
	docker compose -f docker-compose.prod.yml exec backend python manage.py migrate --noinput
	@echo "Collecting static files..."
	docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
	@echo "Production deployment completed!"

# Environment Validation
check-env:
	@echo "Checking environment configuration..."
	@test -f .env || (echo "ERROR: .env file not found! Copy .env.example to .env" && exit 1)
	@grep -q "change-me" .env && (echo "ERROR: Please update default values in .env file!" && exit 1) || true
	@echo "Environment configuration OK"

# Utilities
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned temporary files and caches"

# Create superuser
createsuperuser:
	docker compose exec backend python manage.py createsuperuser

# Database backup (development)
backup-db:
	docker compose exec db pg_dump -U $(shell grep POSTGRES_USER .env | cut -d '=' -f2) $(shell grep POSTGRES_DB .env | cut -d '=' -f2) > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backup created"

# Health check
health:
	@curl -f http://localhost:8000/health/ || echo "Health check failed"
