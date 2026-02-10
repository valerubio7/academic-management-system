#!/bin/sh
set -e

# Resolve database connection variables (Railway PG* || Docker Compose vars)
DB_HOST="${PGHOST:-${DATABASE_HOST}}"
DB_PORT="${PGPORT:-${DATABASE_PORT:-5432}}"
DB_USER="${PGUSER:-${POSTGRES_USER}}"
DB_PASS="${PGPASSWORD:-${POSTGRES_PASSWORD}}"
DB_NAME="${PGDATABASE:-${POSTGRES_DB}}"

echo "==> Waiting for PostgreSQL to be ready..."
until python -c "import psycopg2; psycopg2.connect(host='${DB_HOST}', port='${DB_PORT}', user='${DB_USER}', password='${DB_PASS}', dbname='${DB_NAME}')" 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "==> PostgreSQL is up - continuing..."

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Creating superuser if it doesn't exist..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: username=admin, password=admin123')
else:
    print('Superuser already exists')
EOF

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Starting application..."
exec "$@"
