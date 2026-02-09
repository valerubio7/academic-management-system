# 🐳 Deployment Guide - Academic Management System

Esta guía explica cómo desplegar el Academic Management System usando Docker Compose en diferentes entornos.

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Configuración Inicial](#configuración-inicial)
- [Deployment Local (Desarrollo)](#deployment-local-desarrollo)
- [Deployment Producción](#deployment-producción)
- [Operaciones Comunes](#operaciones-comunes)
- [Monitoreo y Logs](#monitoreo-y-logs)
- [Backup y Restauración](#backup-y-restauración)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Requisitos Previos

### Software Necesario

- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0
- **Make** (opcional, para comandos simplificados)

### Verificar Instalación

```bash
docker --version
docker-compose --version
make --version  # opcional
```

---

## ⚙️ Configuración Inicial

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd academic-management-system
```

### 2. Configurar Variables de Entorno

#### Para Desarrollo

```bash
cp .env.example .env
```

Editar `.env` con configuración de desarrollo (DEBUG=True).

#### Para Producción

```bash
cp .env.production.example .env.production
```

**⚠️ IMPORTANTE:** Actualizar los siguientes valores en `.env.production`:

```bash
# Generar SECRET_KEY único
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Actualizar en .env.production:
SECRET_KEY=<tu-secret-key-generado>
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
POSTGRES_PASSWORD=<password-seguro>
CSRF_TRUSTED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
```

### 3. Permisos del Entrypoint Script

```bash
chmod +x docker-entrypoint.sh
```

---

## 🚀 Deployment Local (Desarrollo)

### Usando Make (Recomendado)

```bash
# Iniciar servicios
make dev-up

# Ver logs
make dev-logs

# Detener servicios
make dev-down
```

### Usando Docker Compose Directamente

```bash
# Iniciar servicios (DB + Django)
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Detener servicios
docker-compose down
```

### Acceder a la Aplicación

- **URL**: http://localhost:8000
- **Admin**: http://localhost:8000/admin/
  - Usuario: `admin`
  - Password: `admin123`

---

## 🏢 Deployment Producción

### 1. Preparar Entorno de Producción

```bash
# Usar archivo .env.production
cp .env.production .env

# Construir imágenes
make prod-build
# O:
docker-compose build --no-cache
```

### 2. Iniciar Servicios en Producción

```bash
# Iniciar todos los servicios
make prod-up
# O:
docker-compose up -d
```

### 3. Verificar Servicios

```bash
# Ver estado
make status
# O:
docker-compose ps

# Ver logs
make prod-logs
```

### 4. Acceder a la Aplicación

- **HTTP**: http://tu-dominio.com:8000
- **Admin**: http://tu-dominio.com:8000/admin/

---

## 🔄 Operaciones Comunes

### Migraciones de Base de Datos

```bash
# Ejecutar migraciones
make migrate
# O:
docker-compose exec web python manage.py migrate

# Crear nuevas migraciones
make makemigrations
# O:
docker-compose exec web python manage.py makemigrations
```

### Crear Superusuario

```bash
make superuser
# O:
docker-compose exec web python manage.py createsuperuser
```

### Ejecutar Tests

```bash
# Tests básicos
make test

# Tests con coverage
make test-coverage
```

### Recolectar Archivos Estáticos

```bash
make collectstatic
# O:
docker-compose exec web python manage.py collectstatic --noinput
```

### Acceder a Shell

```bash
# Shell de Django
make shell

# Shell del contenedor
docker-compose exec web sh

# Shell de PostgreSQL
make db-shell
```

---

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Logs de todos los servicios
docker-compose logs -f

# Logs de Django
make logs-web
# O:
docker-compose logs -f web

# Logs de PostgreSQL
make logs-db
```

### Ubicación de Logs en el Contenedor

- **Django**: `/app/logs/django.log` (en producción)

### Health Checks

```bash
# Verificar health check de Django
curl http://localhost:8000/health/
```

---

## 💾 Backup y Restauración

### Crear Backup de Base de Datos

```bash
make backup-db
# O:
mkdir -p backups
docker-compose exec -T db pg_dump -U admin AMSdatabase > backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restaurar Base de Datos

```bash
# Usar Make (interactivo)
make restore-db

# Manualmente
docker-compose exec -T db psql -U admin AMSdatabase < backups/backup_YYYYMMDD_HHMMSS.sql
```

### Backup de Archivos Media

```bash
# Crear backup
docker run --rm -v ams_media_files:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restaurar backup
docker run --rm -v ams_media_files:/data -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/media_backup_YYYYMMDD_HHMMSS.tar.gz -C /data
```

---

## 🐛 Troubleshooting

### Problema: Contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs web

# Verificar configuración
docker-compose config
```

### Problema: Error de conexión a PostgreSQL

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps db

# Verificar health check
docker-compose exec db pg_isready -U admin

# Reiniciar base de datos
docker-compose restart db
```

### Problema: Migraciones fallan

```bash
# Verificar estado de migraciones
docker-compose exec web python manage.py showmigrations

# Hacer fake de migración específica (si es necesario)
docker-compose exec web python manage.py migrate --fake app_name migration_name
```

### Problema: Puerto 8000 ocupado

```bash
# Ver qué proceso usa el puerto
sudo lsof -i :8000

# Cambiar puerto en .env
WEB_PORT=8001
```

### Problema: Permisos en volúmenes

```bash
# Verificar permisos
docker-compose exec web ls -la /app/media

# Arreglar permisos
docker-compose exec web chown -R appuser:appuser /app/media
```

### Limpiar Todo y Empezar de Nuevo

```bash
# Detener y eliminar contenedores, volúmenes
make clean-docker
# O:
docker-compose down -v
docker system prune -af
docker volume prune -f

# Reconstruir
docker-compose build --no-cache
docker-compose up -d
```

---

## 📈 Optimización para Producción

### 1. Configurar Workers de Gunicorn

Editar `docker-compose.yml`:

```yaml
args:
  WORKERS: 4  # Fórmula: (2 x CPU cores) + 1
  TIMEOUT: 30
```

### 2. Configurar Redis para Caché (Opcional)

Agregar servicio Redis en `docker-compose.yml`:

```yaml
redis:
  image: redis:7-alpine
  container_name: ams_redis
  restart: unless-stopped
  volumes:
    - redis_data:/data
  networks:
    - ams_network
```

Actualizar `.env`:
```bash
REDIS_URL=redis://redis:6379/0
```

### 3. Configurar Límites de Recursos

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      memory: 512M
```

---

## 📝 Checklist de Deployment a Producción

- [ ] Generar nuevo `SECRET_KEY`
- [ ] Configurar `DEBUG=False`
- [ ] Actualizar `ALLOWED_HOSTS` con dominio real
- [ ] Configurar `CSRF_TRUSTED_ORIGINS`
- [ ] Usar contraseñas seguras para PostgreSQL
- [ ] Configurar backups automáticos
- [ ] Configurar monitoreo (Sentry, etc.)
- [ ] Revisar logs de producción
- [ ] Configurar firewall
- [ ] Probar health checks
- [ ] Documentar credenciales de forma segura

---

## 🔗 Referencias

- [Docker Documentation](https://docs.docker.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/settings.html)

---

## 📞 Soporte

Para problemas o preguntas, consultar:
- Documentación del proyecto
- Issues en GitHub
- Logs de aplicación en `/app/logs/`
