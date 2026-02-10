# Academic Management System

Sistema de gestion academica desarrollado con Django, orientado al modelo universitario argentino. Permite administrar facultades, carreras, materias, inscripciones a cursado y mesas de examen final, y calificaciones, con roles diferenciados para administradores, profesores y estudiantes.

## Tabla de Contenidos

- [Tecnologias](#tecnologias)
- [Arquitectura](#arquitectura)
- [Modelo de Datos](#modelo-de-datos)
- [Roles y Permisos](#roles-y-permisos)
- [Rutas de la Aplicacion](#rutas-de-la-aplicacion)
- [Requisitos Previos](#requisitos-previos)
- [Instalacion y Ejecucion](#instalacion-y-ejecucion)
- [Comandos Utiles](#comandos-utiles)
- [Variables de Entorno](#variables-de-entorno)
- [Datos de Prueba](#datos-de-prueba)
- [Testing](#testing)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Despliegue en Railway](#despliegue-en-railway)
- [Licencia](#licencia)

## Tecnologias

| Componente | Tecnologia |
|---|---|
| Lenguaje | Python 3.14 |
| Framework | Django 5.2 |
| Base de datos (dev) | SQLite3 |
| Base de datos (prod) | PostgreSQL 18.1 |
| ORM | Django ORM |
| Servidor web (prod) | Gunicorn |
| Archivos estaticos | WhiteNoise |
| Gestor de paquetes | uv (hatchling build) |
| Contenedores | Docker + Docker Compose |
| Testing | pytest + pytest-django + pytest-cov |
| Linting / Formato | Ruff (lint + format), mypy |
| Frontend | Bootstrap 5.3 (tema oscuro) |

## Arquitectura

El proyecto sigue un patron **MTV (Model-Template-View) con capa de servicios**, organizado en cuatro aplicaciones Django alineadas al dominio:

```
config/          Configuracion del proyecto (settings, URLs raiz, WSGI/ASGI, health check)
users/           Gestion de usuarios y autenticacion
academics/       Estructura academica (facultades, carreras, materias)
enrollments/     Inscripciones a cursado y mesas de examen final
grading/         Calificaciones y estados academicos
tests/           Suite de tests centralizada
templates/       Templates HTML (Bootstrap 5 dark theme)
static/          Archivos estaticos (CSS)
```

**Patrones destacados:**

- **Capa de servicios**: La logica de negocio esta encapsulada en clases `*Service` (`UserService`, `AssignmentService`, `EnrollmentService`, `GradeService`), manteniendo las vistas delgadas.
- **Transacciones atomicas**: Todas las operaciones de escritura en servicios usan `@transaction.atomic`.
- **Mixins de acceso por rol**: `AdministratorRequiredMixin`, `ProfessorRequiredMixin`, `StudentRequiredMixin` controlan el acceso a las vistas.
- **Excepcion unificada**: `ServiceError` como unica excepcion de la capa de servicios, con campos estructurados (`service`, `operation`, `message`, `original_exception`).
- **Vistas CRUD base**: La app `academics` define `BaseCreateView`, `BaseUpdateView`, `BaseDeleteView` para reducir repeticion.
- **Auto-backfill de notas**: Al consultar calificaciones, `GradeService` crea automaticamente registros `Grade` faltantes para alumnos inscriptos.

## Modelo de Datos

```
Faculty 1───* Career 1───* Subject *───* Professor (M2M)
                │               │
                │               ├───* FinalExam *───* Professor (M2M)
                │               │        │
                │               │        └── FinalExamInscription ──* Student
                │               │
                │               ├── SubjectInscription ──* Student
                │               │
                │               └── Grade ──* Student
                │
                └── Student ──1 CustomUser
                    Professor ──1 CustomUser
                    Administrator ──1 CustomUser
```

### Entidades principales

**CustomUser** (extiende AbstractUser): Campos base de Django + `role` (administrator/professor/student), `dni` (unico), `phone`, `birth_date`, `address`.

**Student**: `student_id` (PK), `user` (1:1 -> CustomUser), `career` (FK -> Career), `enrollment_date`.

**Professor**: `professor_id` (PK), `user` (1:1 -> CustomUser), `subjects` (M2M -> Subject), `final_exams` (M2M -> FinalExam), `degree`, `hire_date`, `category` (titular/adjunct/auxiliar).

**Administrator**: `administrator_id` (PK), `user` (1:1 -> CustomUser), `position`, `hire_date`.

**Faculty**: `code` (PK), `name`, `address`, `phone`, `email`, `website`, `dean`, `established_date`, `description`.

**Career**: `code` (PK), `name`, `faculty` (FK -> Faculty), `director`, `duration_years`, `description`.

**Subject**: `code` (PK), `name`, `career` (FK -> Career), `year`, `category` (obligatory/elective), `period` (first/second/annual), `semanal_hours`, `description`.

**FinalExam**: `id` (PK), `subject` (FK -> Subject), `date`, `location`, `duration`, `call_number`, `notes`.

**SubjectInscription**: `student` (FK), `subject` (FK), `inscription_date` (auto). Constraint: unique(student, subject).

**FinalExamInscription**: `student` (FK), `final_exam` (FK), `inscription_date` (auto). Constraint: unique(student, final_exam).

**Grade**: `student` (FK), `subject` (FK), `promotion_grade`, `status` (free/regular/promoted), `final_grade`, `last_updated` (auto), `notes`. Constraint: unique(student, subject). Logica de estado automatica: `final_grade >= 6.0` -> promoted, `< 6.0` -> regular, `None` -> free.

## Roles y Permisos

| Rol | Acceso |
|---|---|
| **Administrador** | CRUD de usuarios, facultades, carreras, materias, mesas de examen final. Asignar profesores a materias y mesas. Dashboard con estadisticas generales. |
| **Profesor** | Ver y editar calificaciones de las materias asignadas. Ver inscriptos a sus mesas de examen final. Dashboard con sus materias y mesas. |
| **Estudiante** | Inscribirse a materias y mesas de examen final. Ver sus inscripciones y materias disponibles. Dashboard personalizado. |

La autenticacion es por sesion (Django auth). El acceso se controla mediante mixins que verifican el campo `role` del usuario.

## Rutas de la Aplicacion

### Autenticacion y General

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/` | Pagina de inicio |
| GET/POST | `/login/` | Inicio de sesion |
| GET | `/logout/` | Cierre de sesion |
| GET | `/health/` | Health check (monitoreo) |

### Panel de Administrador

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/admin/dashboard/` | Dashboard del administrador |
| GET | `/admin/users/` | Lista de usuarios |
| GET/POST | `/admin/users/create/` | Crear usuario |
| GET/POST | `/admin/users/<pk>/edit/` | Editar usuario |
| GET/POST | `/admin/users/<pk>/delete/` | Eliminar usuario |
| GET | `/admin/faculties/` | Lista de facultades |
| GET/POST | `/admin/faculties/create/` | Crear facultad |
| GET/POST | `/admin/faculties/<code>/edit/` | Editar facultad |
| GET/POST | `/admin/faculties/<code>/delete/` | Eliminar facultad |
| GET | `/admin/careers/` | Lista de carreras |
| GET/POST | `/admin/careers/create/` | Crear carrera |
| GET/POST | `/admin/careers/<code>/edit/` | Editar carrera |
| GET/POST | `/admin/careers/<code>/delete/` | Eliminar carrera |
| GET | `/admin/subjects/` | Lista de materias |
| GET/POST | `/admin/subjects/create/` | Crear materia |
| GET/POST | `/admin/subjects/<code>/edit/` | Editar materia |
| GET/POST | `/admin/subjects/<code>/delete/` | Eliminar materia |
| GET/POST | `/admin/subjects/<code>/assign-professors/` | Asignar profesores a materia |
| GET | `/admin/finals/` | Lista de mesas de examen final |
| GET/POST | `/admin/finals/create/` | Crear mesa de examen final |
| GET/POST | `/admin/finals/<pk>/edit/` | Editar mesa de examen final |
| GET/POST | `/admin/finals/<pk>/delete/` | Eliminar mesa de examen final |
| GET/POST | `/admin/finals/<pk>/assign-professors/` | Asignar profesores a mesa |

### Panel de Profesor

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/professor/dashboard/` | Dashboard del profesor |
| GET | `/professor/subjects/<code>/grades/` | Calificaciones de una materia |
| GET/POST | `/professor/grades/<pk>/edit/` | Editar calificacion |
| GET | `/professor/finals/<pk>/inscriptions/` | Ver inscriptos a mesa de final |

### Panel de Estudiante

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/student/dashboard/` | Dashboard del estudiante |
| GET | `/student/subjects/` | Materias disponibles para inscripcion |
| GET/POST | `/student/subjects/<code>/enroll/` | Inscribirse a materia |
| GET | `/student/finals/` | Mesas de examen final disponibles |
| GET/POST | `/student/finals/<pk>/enroll/` | Inscribirse a mesa de examen final |
| GET | `/student/my-enrollments/` | Mis inscripciones |

## Requisitos Previos

- **Docker** y **Docker Compose** (para ejecucion con contenedores)
- **Python 3.14** y **uv** (para ejecucion local sin Docker)

## Instalacion y Ejecucion

### Con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd academic-management-system

# 2. Crear archivo de entorno
cp .env.example .env
# Editar .env con las configuraciones deseadas

# 3. Construir e iniciar los servicios
docker-compose build --no-cache
docker-compose up -d

# La aplicacion estara disponible en http://localhost:8000
# Se crea automaticamente un superusuario: admin / admin123
```

### Sin Docker (desarrollo local)

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd academic-management-system

# 2. Crear entorno virtual e instalar dependencias
uv sync

# 3. Crear archivo de entorno
cp .env.example .env
# IMPORTANTE: Verificar que DEBUG='True' en .env para usar SQLite.
# Si DEBUG=False, Django intentara conectarse a PostgreSQL.

# 4. Ejecutar migraciones
uv run python manage.py makemigrations
uv run python manage.py migrate

# 5. Crear superusuario
uv run python manage.py createsuperuser

# 6. Iniciar el servidor de desarrollo
uv run python manage.py runserver
```

## Comandos Utiles

### Docker

```bash
# Construir imagenes
docker-compose build --no-cache

# Iniciar / detener servicios
docker-compose up -d
docker-compose down

# Ver logs
docker-compose logs -f web

# Abrir shell en el contenedor
docker-compose exec web sh

# Reiniciar servicios
docker-compose restart

# Estado de los servicios
docker-compose ps

# Limpiar contenedores y volumenes
docker-compose down -v
```

### Django (desarrollo local)

```bash
# Migraciones
uv run python manage.py makemigrations
uv run python manage.py migrate

# Crear superusuario
uv run python manage.py createsuperuser

# Shell interactivo
uv run python manage.py shell

# Recolectar archivos estaticos
uv run python manage.py collectstatic --noinput

# Servidor de desarrollo
uv run python manage.py runserver
```

### Django (dentro de Docker)

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py collectstatic --noinput
```

### Base de Datos

```bash
# Backup (PostgreSQL en Docker)
docker-compose exec -T db pg_dump -U admin AMSdatabase > backup.sql

# Restaurar
docker-compose exec -T db psql -U admin AMSdatabase < backup.sql

# Shell de PostgreSQL
docker-compose exec db psql -U admin AMSdatabase
```

## Variables de Entorno

Copiar `.env.example` a `.env` y ajustar los valores.

| Variable | Descripcion | Default |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django (obligatoria en produccion) | `change-me-...` |
| `DEBUG` | Modo debug (`True` = SQLite, `False` = PostgreSQL) | `True` |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | `localhost,127.0.0.1` |
| `POSTGRES_DB` | Nombre de la base de datos PostgreSQL | `AMSdatabase` |
| `POSTGRES_USER` | Usuario de PostgreSQL | `admin` |
| `POSTGRES_PASSWORD` | Contrasena de PostgreSQL | `admin` |
| `DATABASE_HOST` | Host de la base de datos (`db` para Docker) | `db` |
| `DATABASE_PORT` | Puerto de PostgreSQL | `5432` |
| `PGDATABASE` | Nombre de la BD (Railway, sobreescribe `POSTGRES_DB`) | - |
| `PGUSER` | Usuario de la BD (Railway, sobreescribe `POSTGRES_USER`) | - |
| `PGPASSWORD` | Contrasena de la BD (Railway, sobreescribe `POSTGRES_PASSWORD`) | - |
| `PGHOST` | Host de la BD (Railway, sobreescribe `DATABASE_HOST`) | - |
| `PGPORT` | Puerto de la BD (Railway, sobreescribe `DATABASE_PORT`) | - |
| `CSRF_TRUSTED_ORIGINS` | Origenes confiables para CSRF (produccion) | `` |
| `EMAIL_HOST` | Servidor SMTP | `smtp.gmail.com` |
| `EMAIL_PORT` | Puerto SMTP | `587` |
| `EMAIL_USE_TLS` | Usar TLS para email | `True` |
| `EMAIL_HOST_USER` | Usuario SMTP | `` |
| `EMAIL_HOST_PASSWORD` | Contrasena SMTP | `` |
| `DEFAULT_FROM_EMAIL` | Email remitente por defecto | `noreply@example.com` |

## Datos de Prueba

El comando `seed_data` puebla la base de datos con datos realistas para desarrollo y testing:

```bash
# Cargar datos de prueba (desarrollo local)
uv run python manage.py seed_data

# Borrar datos existentes y recargar
uv run python manage.py seed_data --flush

# Con Docker
docker-compose exec web python manage.py seed_data
docker-compose exec web python manage.py seed_data --flush
```

### Datos generados

| Entidad | Cantidad |
|---|---|
| Facultades | 3 |
| Carreras | 6 (2 por facultad) |
| Materias | 30 (5 por carrera) |
| Administradores | 2 |
| Profesores | 8 |
| Estudiantes | 20 |
| Mesas de examen final | 15 |
| Inscripciones a materias | ~45 |
| Inscripciones a finales | ~19 |
| Calificaciones | ~45 |

Todos los usuarios usan la contrasena `password123`. Los usernames siguen el patron: `admin1`, `admin2`, `prof1`-`prof8`, `student1`-`student20`.

## Testing

El proyecto utiliza **pytest** con `pytest-django` y `pytest-cov`. Los tests se encuentran centralizados en el directorio `tests/`.

```bash
# Ejecutar todos los tests (local)
uv run pytest tests/ -v

# Ejecutar todos los tests (Docker)
docker-compose exec web python -m pytest tests/ -v

# Ejecutar tests de un modulo especifico
uv run pytest tests/test_users.py -v

# Ejecutar con reporte de cobertura
uv run pytest tests/ --cov=. --cov-report=term --cov-report=html

# Cobertura en Docker
docker-compose exec web python -m pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Cobertura de tests

| Modulo | Contenido testeado |
|---|---|
| `test_users.py` | Modelos de usuario, UserService, AssignmentService, vistas de autenticacion y CRUD |
| `test_academics.py` | Modelos de facultad/carrera/materia, vistas CRUD administrativas |
| `test_enrollments.py` | Modelos de inscripcion, EnrollmentService, vistas de inscripcion |
| `test_grading.py` | Modelo de calificacion, GradeService, vistas de profesor, transiciones de estado |

## Estructura del Proyecto

```
academic-management-system/
├── config/                         # Configuracion Django
│   ├── settings.py                 # Settings principal
│   ├── urls.py                     # URLs raiz
│   ├── health_check.py             # Endpoint /health/
│   ├── wsgi.py                     # WSGI
│   └── asgi.py                     # ASGI
├── users/                          # App: Usuarios
│   ├── models.py                   # CustomUser, Student, Professor, Administrator
│   ├── views.py                    # Login, dashboards, CRUD de usuarios
│   ├── services.py                 # UserService, AssignmentService
│   ├── mixins.py                   # Mixins de control de acceso por rol
│   ├── forms.py                    # Formularios de usuario
│   └── urls.py                     # Rutas de usuarios
├── academics/                      # App: Academica
│   ├── models.py                   # Faculty, Career, Subject
│   ├── views.py                    # CRUD de facultades, carreras, materias
│   ├── forms.py                    # Formularios academicos
│   └── urls.py                     # Rutas academicas
├── enrollments/                    # App: Inscripciones
│   ├── models.py                   # FinalExam, SubjectInscription, FinalExamInscription
│   ├── views.py                    # CRUD de finales, inscripcion de estudiantes
│   ├── services.py                 # EnrollmentService
│   ├── forms.py                    # Formulario de mesa de final
│   └── urls.py                     # Rutas de inscripciones
├── grading/                        # App: Calificaciones
│   ├── models.py                   # Grade
│   ├── views.py                    # Lista y edicion de calificaciones
│   ├── services.py                 # GradeService
│   ├── forms.py                    # Formulario de calificacion
│   └── urls.py                     # Rutas de calificaciones
├── tests/                          # Tests centralizados
│   ├── conftest.py                 # Fixtures compartidos
│   ├── test_users.py
│   ├── test_academics.py
│   ├── test_enrollments.py
│   └── test_grading.py
├── templates/                      # Templates HTML (32 archivos)
│   ├── base.html                   # Layout base (Bootstrap 5 dark)
│   ├── home.html                   # Pagina de inicio
│   ├── 403.html / 404.html / 500.html
│   ├── users/                      # Templates de usuarios
│   ├── academics/                  # Templates academicos
│   ├── enrollments/                # Templates de inscripciones
│   └── grading/                    # Templates de calificaciones
├── static/css/style.css            # Estilos personalizados
├── exceptions.py                   # ServiceError compartido
├── Dockerfile                      # Imagen Docker (Alpine + Gunicorn)
├── docker-compose.yml              # PostgreSQL + Django
├── docker-entrypoint.sh            # Script de inicio del contenedor
├── railway.toml                    # Configuracion de despliegue en Railway
├── pyproject.toml                  # Dependencias y configuracion de herramientas
├── .env.example                    # Template de variables de entorno
└── manage.py                       # Entry point de Django
```

## Despliegue en Railway

El proyecto esta preparado para despliegue en [Railway](https://railway.app/) usando el Dockerfile existente.

### Pasos

1. **Crear proyecto en Railway**: Desde el dashboard de Railway, crear un nuevo proyecto.

2. **Agregar servicio PostgreSQL**: Agregar un servicio de PostgreSQL al proyecto. Railway asigna automaticamente las variables `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGHOST` y `PGPORT`.

3. **Conectar repositorio GitHub**: Agregar un nuevo servicio desde el repositorio de GitHub. Railway detecta el `Dockerfile` automaticamente via `railway.toml`.

4. **Configurar variables de entorno**: En el servicio web, agregar las siguientes variables:

   | Variable | Valor |
   |---|---|
   | `SECRET_KEY` | Una clave secreta unica (generar con `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | `healthcheck.railway.app,.railway.app` |
   | `CSRF_TRUSTED_ORIGINS` | `https://<tu-dominio>.railway.app` |
   | `PGDATABASE` | `${{Postgres.PGDATABASE}}` |
   | `PGUSER` | `${{Postgres.PGUSER}}` |
   | `PGPASSWORD` | `${{Postgres.PGPASSWORD}}` |
   | `PGHOST` | `${{Postgres.PGHOST}}` |
   | `PGPORT` | `${{Postgres.PGPORT}}` |

5. **Generar dominio publico**: En Settings > Networking del servicio web, generar un dominio publico. Actualizar `CSRF_TRUSTED_ORIGINS` con el dominio asignado.

Railway ejecuta automaticamente las migraciones y `collectstatic` a traves del `docker-entrypoint.sh`. El health check se configura via `railway.toml` apuntando a `/health/`.

## Licencia

Este proyecto esta licenciado bajo la **GNU General Public License v3.0**. Ver el archivo [LICENSE](LICENSE) para mas detalles.
