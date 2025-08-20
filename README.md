Academic Management System
==========================

A web-based platform to manage academic operations for universities and colleges. It supports multiple roles (administrator, professor, student), academic structure (faculties, careers, subjects), enrollments, grading, and certificate generation.

Features
--------

- User authentication and roles (administrator, professor, student)
- Admin dashboard: CRUD for users, faculties, careers, subjects, final exams
- Assign professors to subjects and finals
- Student dashboard: subject and final exam inscriptions, grade tracking
- Professor dashboard: manage grades and view final inscriptions
- Regular student certificate generation (DOCX via docxtpl)
- Role-based access control (decorators/checks)

Tech Stack
---------

- Backend: Python 3, Django
- Frontend: Django Templates, HTML5, CSS, JavaScript
- Database: PostgreSQL by default (configurable via environment variables)
- Containerization: Docker + docker-compose
- Documents: docxtpl for generating certificates

Project Structure
-----------------

```text
academics/         # Academic models, forms, admin, tests
accounts/          # Auth views, login form, URLs
inscriptions/      # Subject and final exam enrollment models/admin
main/              # Django project settings, URLs, ASGI/WSGI
users/             # CustomUser, profiles, views, admin, templates
static/            # CSS, JS
templates/         # Base templates
docs/              # Diagrams and documentation assets
manage.py
requirements.txt
docker-compose.yml
Dockerfile
```

Getting Started
---------------

Prerequisites
-------------

- Python 3.10+
- pip
- Docker (optional)

Environment Variables
---------------------

The app reads configuration from a `.env` file (loaded in `main/settings.py`).

Minimal variables:

```bash
SECRET_KEY=dev-secret
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL settings (required)
POSTGRES_DB=ams
POSTGRES_USER=ams
POSTGRES_PASSWORD=ams
# Use `db` when running with docker-compose, or `localhost` if Postgres runs locally
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

Local Setup
-----------

<!-- markdownlint-disable MD029 -->

1. Create and activate a virtual environment

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

2. Install dependencies

  ```bash
  pip install -r requirements.txt
  ```

3. Configure environment variables (dotenv is read in ``main/settings.py``)

  Create a ``.env`` in the project root:

  ```bash
  SECRET_KEY=dev-secret
  DEBUG=1
  ALLOWED_HOSTS=localhost,127.0.0.1
  POSTGRES_DB=ams
  POSTGRES_USER=ams
  POSTGRES_PASSWORD=ams
  DATABASE_HOST=localhost
  DATABASE_PORT=5432
  ```

4. Apply migrations

  ```bash
  python manage.py migrate
  ```

5. Create an admin user (Django superuser)

  ```bash
  python manage.py createsuperuser
  ```

6. Run the development server

  ```bash
  python manage.py runserver
  ```

7. Access the app at <http://localhost:8000/>

<!-- markdownlint-enable MD029 -->

Docker Setup (optional)
-----------------------

Build and start services:

```bash
docker compose up --build
```

Stop services:

```bash
docker compose down
```

Notes:

- Ensure `.env` includes database credentials and set `DATABASE_HOST=db` for docker-compose.
- The `backend` service binds the project folder as a volume for development.

Core Workflows
--------------

- Admin:
  - Manage users and their profiles (student, professor, administrator)
  - Maintain faculties, careers, subjects
  - Create and manage final exams
  - Assign professors to subjects and finals

- Student:
  - Enroll in subjects and final exams
  - See grades and eligibility for finals
  - Download regular student certificate (template: ``regular_certificate.docx`` at repo root)

- Professor:
  - View assigned subjects and finals
  - Enter and update student grades
  - View inscriptions for assigned final exams

Routes
------

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
- Student regular certificate: `/student/certificate/regular/`
- Professor dashboard: `/professor/dashboard/`

Configuration Notes
-------------------

- Environment variables are loaded via ``.env`` (see ``main/settings.py``)
- Default database is PostgreSQL (see `DATABASES` in ``main/settings.py``). For local Postgres, set `DATABASE_HOST=localhost`; for docker-compose, set `DATABASE_HOST=db`.
- The regular certificate uses ``docxtpl`` and the ``regular_certificate.docx`` template. Adjust placeholders in the template to match context variables in ``users.views.download_regular_certificate``.

Testing
-------

Run the test suite:

```bash
python manage.py test
```

Documentation
-------------

- Code is documented with Google-style docstrings across apps.
- Optionally, you can add Sphinx to generate HTML documentation from docstrings.

License
-------

GPLv3. See the ``LICENSE`` file for details.
