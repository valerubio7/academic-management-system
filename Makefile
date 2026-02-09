# Makefile para Academic Management System
# Facilita operaciones comunes de desarrollo y producción

.PHONY: help dev-up dev-down prod-up prod-down prod-build logs shell test migrate clean

# Mostrar ayuda por defecto
help:
	@echo "Academic Management System - Comandos Disponibles"
	@echo "=================================================="
	@echo ""
	@echo "DESARROLLO:"
	@echo "  make dev-up          - Iniciar servicios en modo desarrollo"
	@echo "  make dev-down        - Detener servicios de desarrollo"
	@echo "  make dev-logs        - Ver logs de desarrollo"
	@echo "  make dev-shell       - Abrir shell en contenedor Django"
	@echo ""
	@echo "PRODUCCIÓN:"
	@echo "  make prod-up         - Iniciar servicios en modo producción"
	@echo "  make prod-down       - Detener servicios de producción"
	@echo "  make prod-build      - Construir imágenes de producción"
	@echo "  make prod-logs       - Ver logs de producción"
	@echo ""
	@echo "UTILIDADES:"
	@echo "  make test            - Ejecutar tests"
	@echo "  make migrate         - Ejecutar migraciones de base de datos"
	@echo "  make makemigrations  - Crear nuevas migraciones"
	@echo "  make superuser       - Crear superusuario"
	@echo "  make shell           - Abrir shell de Django"
	@echo "  make clean           - Limpiar archivos temporales y caches"
	@echo "  make backup-db       - Hacer backup de la base de datos"
	@echo "  make restore-db      - Restaurar base de datos desde backup"
	@echo ""

# =================================================================
# DESARROLLO
# =================================================================

dev-up:
	@echo "Iniciando servicios en modo desarrollo..."
	docker-compose up -d
	@echo "✓ Servicios iniciados"
	@echo "Django: http://localhost:8000"

dev-down:
	@echo "Deteniendo servicios de desarrollo..."
	docker-compose down
	@echo "✓ Servicios detenidos"

dev-logs:
	docker-compose logs -f web

dev-shell:
	docker-compose exec web sh

# =================================================================
# PRODUCCIÓN
# =================================================================

prod-up:
	@echo "Iniciando servicios en modo producción..."
	docker-compose up -d
	@echo "✓ Servicios iniciados"
	@echo "Aplicación: http://localhost:8000"

prod-down:
	@echo "Deteniendo servicios de producción..."
	docker-compose down
	@echo "✓ Servicios detenidos"

prod-build:
	@echo "Construyendo imágenes de producción..."
	docker-compose build --no-cache
	@echo "✓ Imágenes construidas"

prod-logs:
	docker-compose logs -f

prod-restart:
	@echo "Reiniciando servicios de producción..."
	docker-compose restart
	@echo "✓ Servicios reiniciados"

# =================================================================
# UTILIDADES
# =================================================================

test:
	@echo "Ejecutando tests..."
	docker-compose exec web python -m pytest tests/ -v

test-coverage:
	@echo "Ejecutando tests con coverage..."
	docker-compose exec web python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

migrate:
	@echo "Ejecutando migraciones..."
	docker-compose exec web python manage.py migrate

makemigrations:
	@echo "Creando migraciones..."
	docker-compose exec web python manage.py makemigrations

superuser:
	@echo "Creando superusuario..."
	docker-compose exec web python manage.py createsuperuser

shell:
	@echo "Abriendo shell de Django..."
	docker-compose exec web python manage.py shell

collectstatic:
	@echo "Recolectando archivos estáticos..."
	docker-compose exec web python manage.py collectstatic --noinput

# =================================================================
# BASE DE DATOS
# =================================================================

backup-db:
	@echo "Creando backup de base de datos..."
	@mkdir -p backups
	docker-compose exec -T db pg_dump -U $${POSTGRES_USER:-admin} $${POSTGRES_DB:-AMSdatabase} > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✓ Backup creado en backups/"

restore-db:
	@echo "Restaurando base de datos..."
	@read -p "Archivo de backup: " BACKUP_FILE; \
	docker-compose exec -T db psql -U $${POSTGRES_USER:-admin} $${POSTGRES_DB:-AMSdatabase} < $$BACKUP_FILE
	@echo "✓ Base de datos restaurada"

db-shell:
	@echo "Abriendo shell de PostgreSQL..."
	docker-compose exec db psql -U $${POSTGRES_USER:-admin} $${POSTGRES_DB:-AMSdatabase}

# =================================================================
# LIMPIEZA
# =================================================================

clean:
	@echo "Limpiando archivos temporales..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "✓ Limpieza completada"

clean-docker:
	@echo "Limpiando contenedores y volúmenes..."
	docker-compose down -v
	docker system prune -f
	@echo "✓ Docker limpiado"

# =================================================================
# INFORMACIÓN
# =================================================================

status:
	@echo "Estado de los servicios:"
	docker-compose ps

logs-db:
	docker-compose logs -f db

logs-web:
	docker-compose logs -f web
