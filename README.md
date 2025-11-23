# Academic Management System

A production-ready web-based platform to manage academic operations for universities and colleges. It supports multiple roles (administrator, professor, student), academic structure (faculties, careers, subjects), enrollments, and grading.

## Features

- User authentication and roles (administrator, professor, student)
- Admin dashboard: CRUD for users, faculties, careers, subjects, final exams
- Assign professors to subjects and finals
- Student dashboard: subject and final exam inscriptions, grade tracking
- Professor dashboard: manage grades and view final inscriptions
- Role-based access control (decorators/checks)
- Health check endpoint for monitoring
- Production-ready security settings
- Static files serving with WhiteNoise
- Comprehensive logging system
- Database connection pooling
- Email notification support

## Tech Stack

- Backend: Python 3.12, Django 5.2.3
- Frontend: Django Templates, HTML5, CSS, JavaScript
- Database: PostgreSQL 16 with optimized indexes
- Web Server: Gunicorn (production)
- Static Files: WhiteNoise
- Containerization: Docker + docker-compose
- Optional: Redis (caching), Nginx (reverse proxy)

## Project Structure

```text
app/                    # Main Django app
  models/              # Database models (Student, Professor, Grade, etc.)
  views/               # Views for admin, student, professor
  services/            # Business logic layer
  repositories/        # Data access layer
  forms/               # Django forms
  migrations/          # Database migrations
config/                # Django project settings
  settings.py         # Main configuration file
  urls.py             # URL routing
  wsgi.py             # WSGI application
  health_check.py     # Health check endpoint
templates/             # HTML templates
  404.html            # Custom 404 error page
  500.html            # Custom 500 error page
  403.html            # Custom 403 error page
static/                # CSS, JS, images
tests/                 # Comprehensive test suite
docs/                  # Documentation and diagrams
requirements.txt       # Python dependencies
Makefile              # Common commands
.env.example          # Environment variables template
docker-compose.yml    # Development environment
docker-compose.prod.yml # Production environment
Dockerfile            # Production-ready Docker image
manage.py             # Django management script
```

## Getting Started

### Prerequisites

- Docker and Docker Compose (recommended)
- OR: Python 3.12+, pip, PostgreSQL 16+

### Quick Start with Docker (Recommended)

1. **Clone the repository**

```bash
git clone <repository-url>
cd academic-management-system
```

2. **Set up environment variables**

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and update the values (at minimum, change SECRET_KEY and passwords)
nano .env  # or use your preferred editor
```

3. **Generate a secure SECRET_KEY**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and update `SECRET_KEY` in your `.env` file.

4. **Start development environment**

```bash
# Build and start services
docker compose up --build -d

# Apply database migrations
make migrate

# Create a superuser
docker compose exec backend python manage.py createsuperuser

# Access the application at http://localhost:8000
```

5. **Useful commands** (using Makefile)

```bash
make help            # Show all available commands
make logs            # View application logs
make shell           # Open Django shell
make test            # Run test suite
make migrate         # Apply migrations
make collectstatic   # Collect static files
```

### Local Development Setup (Without Docker)

1. **Create and activate a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL database**

Create a database and user in PostgreSQL:

```sql
CREATE DATABASE academic_management_system;
CREATE USER ams_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE academic_management_system TO ams_user;
```

4. **Configure environment variables**

Create a `.env` file in the project root:

```bash
cp .env.example .env
# Edit .env with your actual values
```

5. **Apply migrations**

```bash
python manage.py migrate
```

6. **Collect static files**

```bash
python manage.py collectstatic --noinput
```

7. **Create an admin user**

```bash
python manage.py createsuperuser
```

8. **Run the development server**

```bash
python manage.py runserver
```

9. **Access the app at http://localhost:8000/**

## Additional Documentation

- Code is documented with Google-style docstrings across all modules
- Class diagrams available in `docs/` directory
- API documentation: Access Django admin at `/django-admin/` for model documentation
- For production deployment details, see `.env.example` and `docker-compose.prod.yml` comments

## Core Workflows

- Admin:

  - Manage users and their profiles (student, professor, administrator)
  - Maintain faculties, careers, subjects
  - Create and manage final exams
  - Assign professors to subjects and finals

- Student:

  - Enroll in subjects and final exams
  - See grades and eligibility for finals

- Professor:
  - View assigned subjects and finals
  - Enter and update student grades
  - View inscriptions for assigned final exams

## Routes

- Home: `/`
- Login: `/login/`
- Logout: `/logout/`
- Django Admin: `/django-admin/`

Users app (role dashboards and admin UI):

- Admin dashboard: `/admin/dashboard/`
- Users CRUD: `/admin/users/`
- Faculties: `/admin/faculties/`
- Careers: `/admin/careers/`
- Subjects: `/admin/subjects/`
- Finals: `/admin/finals/`
- Student dashboard: `/student/dashboard/`
- Professor dashboard: `/professor/dashboard/`

## Configuration Notes

- Environment variables are loaded via `.env` (see `main/settings.py`)
- Default database is PostgreSQL (see `DATABASES` in `main/settings.py`). For local Postgres, set `DATABASE_HOST=localhost`; for docker-compose, set `DATABASE_HOST=db`.

## Testing

Run the comprehensive test suite:

```bash
# Using Docker
make test

# Or directly
docker compose exec backend python manage.py test

# Without Docker
python manage.py test

# Run specific test file
python manage.py test tests.test_academics

# Run with coverage
docker compose exec backend coverage run --source='.' manage.py test
docker compose exec backend coverage report
docker compose exec backend coverage html
```

## Production Deployment

### Pre-Deployment Checklist

Before deploying to production, ensure you have completed these critical steps:

- [ ] **Generate a strong SECRET_KEY** (50+ random characters)
- [ ] **Set DEBUG=False** in production environment
- [ ] **Configure ALLOWED_HOSTS** with your actual domain(s)
- [ ] **Set strong database passwords** (16+ characters)
- [ ] **Configure email settings** for notifications
- [ ] **Set up HTTPS/SSL certificates**
- [ ] **Configure CSRF_TRUSTED_ORIGINS** with your HTTPS domains
- [ ] **Review and update .env with production values**
- [ ] **Set up database backups**
- [ ] **Configure monitoring and logging**
- [ ] **Run migrations on production database**
- [ ] **Collect static files**
- [ ] **Test all critical user workflows**

### Production Deployment with Docker

1. **Prepare environment variables**

```bash
# Copy and edit .env with PRODUCTION values
cp .env.example .env
nano .env
```

**Critical production settings in .env:**

```bash
# MUST be changed for production!
SECRET_KEY=<generate-with-command-below>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Use strong passwords
POSTGRES_PASSWORD=<strong-random-password>

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-app-password

# HTTPS configuration
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

2. **Generate production SECRET_KEY**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

3. **Build and deploy with production configuration**

```bash
# Build production image
docker compose -f docker-compose.prod.yml build

# Start production services
docker compose -f docker-compose.prod.yml up -d

# Check services are healthy
docker compose -f docker-compose.prod.yml ps
```

4. **Run database migrations**

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate --noinput
```

5. **Collect static files**

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

6. **Create superuser**

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

7. **Verify health check**

```bash
curl http://localhost:8000/health/
# Should return: {"status":"healthy","database":"connected"}
```

### Using Makefile for Production

```bash
# Validate environment configuration
make check-env

# Build production image
make build-prod

# Full production deployment (checks env, builds, migrates, collects static)
make deploy-prod

# Check application health
make health
```

### Production Environment Variables Reference

See `.env.example` for a complete list of environment variables with detailed documentation.

**Required variables:**

- `SECRET_KEY` - Django secret key (MUST be unique and strong)
- `DEBUG` - Set to `False` in production
- `ALLOWED_HOSTS` - Comma-separated list of allowed domains
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` - Database credentials
- `DATABASE_HOST`, `DATABASE_PORT` - Database connection details

**Optional but recommended:**

- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` - Email configuration
- `REDIS_URL` - Redis cache URL (improves performance)
- `CSRF_TRUSTED_ORIGINS` - HTTPS origins for CSRF protection
- `SENTRY_DSN` - Error tracking (if using Sentry)

### Production Security Checklist

The application is configured with production-ready security settings when `DEBUG=False`:

✅ **Enabled automatically in production:**

- HTTPS redirect (`SECURE_SSL_REDIRECT=True`)
- HTTP Strict Transport Security (HSTS) for 1 year
- Secure cookie settings (Secure, HttpOnly, SameSite)
- Content type nosniff header
- XSS filter
- X-Frame-Options: DENY
- Referrer policy: same-origin
- Static files compression with WhiteNoise
- Database connection pooling
- Comprehensive logging to files
- CSRF protection

⚠️ **Manual configuration required:**

- SSL/TLS certificates installation
- Firewall configuration
- Database backup schedule
- Monitoring and alerting setup
- Rate limiting (optional but recommended)

### Monitoring and Logging

**Health Check Endpoint:**

- URL: `/health/`
- Returns JSON with status and database connectivity
- Use for load balancer health checks

**Log Files:**

- Location: `logs/django.log` (errors)
- Location: `logs/debug.log` (debug info, development only)
- Rotation: 10MB per file, keeps 5 backups
- Format: Timestamp, level, module, message

**View logs:**

```bash
# Real-time logs
docker compose -f docker-compose.prod.yml logs -f backend

# View log files
docker compose -f docker-compose.prod.yml exec backend tail -f logs/django.log
```

### Database Backups

**Manual backup:**

```bash
# Using Makefile
make backup-db

# Or directly
docker compose -f docker-compose.prod.yml exec db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%Y%m%d).sql
```

**Restore from backup:**

```bash
docker compose -f docker-compose.prod.yml exec -T db psql -U $POSTGRES_USER $POSTGRES_DB < backup_20250101.sql
```

### Scaling and Performance

**Increase Gunicorn workers:**

Edit `Dockerfile` and adjust the `--workers` parameter:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "8", "--timeout", "120", "config.wsgi:application"]
```

Recommended: `workers = (2 * CPU cores) + 1`

**Enable Redis caching:**

1. Uncomment Redis service in `docker-compose.prod.yml`
2. Set `REDIS_URL=redis://redis:6379/1` in `.env`
3. Restart services

**Database optimization:**

- Database indexes are configured on frequently queried fields
- Connection pooling is enabled (CONN_MAX_AGE=600)
- Use `EXPLAIN ANALYZE` on slow queries for optimization

### Troubleshooting Production Issues

**Application won't start:**

1. Check environment variables: `make check-env`
2. Verify SECRET_KEY is set and not using default value
3. Check ALLOWED_HOSTS matches your domain
4. View logs: `docker compose -f docker-compose.prod.yml logs backend`

**Static files not loading:**

1. Run collectstatic: `make collectstatic`
2. Verify WhiteNoise is in MIDDLEWARE
3. Check STATIC_ROOT is set correctly

**Database connection errors:**

1. Verify database credentials in `.env`
2. Check database service is running
3. Test connection: `docker compose -f docker-compose.prod.yml exec backend python manage.py dbshell`

**500 errors:**

1. Check logs: `logs/django.log`
2. Verify all migrations are applied
3. Ensure DEBUG=False and error templates exist

### Production vs Development Differences

| Feature         | Development           | Production               |
| --------------- | --------------------- | ------------------------ |
| Server          | Django runserver      | Gunicorn (4 workers)     |
| DEBUG           | True                  | False                    |
| Static Files    | Django serves         | WhiteNoise compression   |
| Database Port   | Exposed (5432)        | Internal only            |
| Code Volume     | Mounted (live reload) | Baked into image         |
| HTTPS           | Optional              | Required (auto-redirect) |
| Logging         | Console only          | Files + Console + Email  |
| Error Pages     | Django debug          | Custom 404/500 templates |
| Session Cookies | Insecure              | Secure, HttpOnly         |

## Routes

- Home: `/`
- Login: `/login/`
- Logout: `/logout/`
- Health Check: `/health/` (for monitoring)
- Django Admin: `/django-admin/`

App routes (role-based dashboards):

- Admin dashboard: `/admin/dashboard/`
- Users CRUD: `/admin/users/`
- Faculties: `/admin/faculties/`
- Careers: `/admin/careers/`
- Subjects: `/admin/subjects/`
- Finals: `/admin/finals/`
- Student dashboard: `/student/dashboard/`
- Professor dashboard: `/professor/dashboard/`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Development Guidelines:**

- Follow PEP 8 style guide
- Write comprehensive docstrings (Google style)
- Add tests for new features
- Update documentation as needed
- Run tests before committing: `make test`

## Support

For issues, questions, or contributions:

- Open an issue on GitHub
- Contact the development team
- Check existing documentation in `docs/`

## Changelog

### Version 2.0.0 (Production Ready - 2025)

- ✅ Added production-ready security settings
- ✅ Configured WhiteNoise for static files
- ✅ Added comprehensive logging system
- ✅ Implemented database connection pooling
- ✅ Added database indexes for optimization
- ✅ Created health check endpoint
- ✅ Added custom error pages (404, 500, 403)
- ✅ Production Docker configuration
- ✅ Environment variables validation
- ✅ Makefile for common tasks
- ✅ Complete production deployment documentation

### Version 1.0.0 (Initial Release)

- User authentication and role-based access control
- Academic structure management
- Student enrollment system
- Grade management
- Professor assignment

## Documentation

- Code is documented with Google-style docstrings across apps.
- Optionally, you can add Sphinx to generate HTML documentation from docstrings.

## License

GPLv3. See the `LICENSE` file for details.

---

**Academic Management System** - Production-ready platform for academic operations management.

For production deployment assistance, refer to the **Production Deployment** section above or contact the development team.
